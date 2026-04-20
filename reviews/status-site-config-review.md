# Review: `neo4j_graphrag_pipeline/config.py`

Source reviewed: https://github.com/jjuniper-dev/status-site/blob/main/neo4j_graphrag_pipeline/config.py

## What’s good

- Clear separation of concerns via focused dataclasses (`Neo4jConfig`, `EmbeddingConfig`, `LLMConfig`, `IndexConfig`, `SchemaConfig`, `PipelineConfig`).
- Practical env-var driven defaults make local setup easy.
- `default_factory` usage avoids mutable default pitfalls for list fields.

## Main issues to address

1. **Insecure default Neo4j password**
   - `NEO4J_PASSWORD` falls back to literal `"password"`.
   - Recommend requiring explicit password in non-local environments and failing fast if unset.

2. **Unsafe numeric parsing from env vars**
   - Direct `int(...)` / `float(...)` casts will raise at import/instantiation time with opaque errors.
   - Add helper parsers with explicit error messages and optional range checks.

3. **No validation for cross-field constraints**
   - Examples: `chunk_overlap < chunk_size`, positive `dimensions`, positive `max_tokens`.
   - Add `__post_init__` validation methods (or a central validate function).

4. **`similarity_fn` is not configurable**
   - Hardcoded to `"cosine"` with no env override.
   - Add `SIMILARITY_FN` env support and validate allowed values.

5. **Provider/model mismatch risk**
   - Defaults imply OpenAI while also exposing sentence-transformer model (`st_model`), but no provider compatibility checks.
   - Add guardrails so provider-specific fields are validated together.

## Suggested refactor (minimal)

- Add small parsing utilities:
  - `env_int(name, default, min_value=None, max_value=None)`
  - `env_float(name, default, min_value=None, max_value=None)`
  - `env_choice(name, default, allowed)`
- Add `__post_init__` to:
  - `EmbeddingConfig` (dimensions > 0)
  - `LLMConfig` (temperature in [0,2], max_tokens > 0)
  - `SchemaConfig` (`chunk_size > 0`, `0 <= chunk_overlap < chunk_size`)
  - `IndexConfig` (validate `similarity_fn` enum)
- Replace `NEO4J_PASSWORD` fallback with empty default + explicit runtime failure in production mode.

## Optional improvements

- Introduce `APP_ENV` (`dev`/`prod`) and relax strictness only in `dev`.
- Add a `to_safe_dict()` method masking secrets for logging.
- Consider Pydantic/BaseSettings for built-in env parsing + validation if dependency cost is acceptable.

## Complete implementation template (dev-relaxed, prod-strict)

Use this drop-in `config.py` pattern to fully address all issues above, including strict password requirements outside development:

```python
from dataclasses import dataclass, field
import os
from typing import Any


def env_str(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def env_int(
    name: str,
    default: int,
    *,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        value = default
    else:
        try:
            value = int(raw)
        except ValueError as exc:
            raise ValueError(f"{name} must be an integer, got: {raw!r}") from exc

    if min_value is not None and value < min_value:
        raise ValueError(f"{name} must be >= {min_value}, got: {value}")
    if max_value is not None and value > max_value:
        raise ValueError(f"{name} must be <= {max_value}, got: {value}")
    return value


def env_float(
    name: str,
    default: float,
    *,
    min_value: float | None = None,
    max_value: float | None = None,
) -> float:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        value = default
    else:
        try:
            value = float(raw)
        except ValueError as exc:
            raise ValueError(f"{name} must be a float, got: {raw!r}") from exc

    if min_value is not None and value < min_value:
        raise ValueError(f"{name} must be >= {min_value}, got: {value}")
    if max_value is not None and value > max_value:
        raise ValueError(f"{name} must be <= {max_value}, got: {value}")
    return value


def env_choice(name: str, default: str, allowed: set[str]) -> str:
    value = env_str(name, default).lower()
    if value not in allowed:
        raise ValueError(f"{name} must be one of {sorted(allowed)}, got: {value!r}")
    return value


@dataclass
class AppConfig:
    app_env: str = field(default_factory=lambda: env_choice("APP_ENV", "dev", {"dev", "prod"}))


@dataclass
class Neo4jConfig:
    uri: str = field(default_factory=lambda: env_str("NEO4J_URI", "bolt://localhost:7687"))
    username: str = field(default_factory=lambda: env_str("NEO4J_USERNAME", "neo4j"))
    password: str = field(default_factory=lambda: env_str("NEO4J_PASSWORD", ""))


@dataclass
class EmbeddingConfig:
    provider: str = field(default_factory=lambda: env_choice("EMBEDDING_PROVIDER", "openai", {"openai", "sentence_transformers"}))
    model: str = field(default_factory=lambda: env_str("EMBEDDING_MODEL", "text-embedding-3-small"))
    st_model: str = field(default_factory=lambda: env_str("ST_MODEL", "all-MiniLM-L6-v2"))
    dimensions: int = field(default_factory=lambda: env_int("EMBEDDING_DIMENSIONS", 1536, min_value=1))

    def __post_init__(self) -> None:
        if self.provider == "openai" and not self.model:
            raise ValueError("EMBEDDING_MODEL must be set when EMBEDDING_PROVIDER=openai")
        if self.provider == "sentence_transformers" and not self.st_model:
            raise ValueError("ST_MODEL must be set when EMBEDDING_PROVIDER=sentence_transformers")


@dataclass
class LLMConfig:
    provider: str = field(default_factory=lambda: env_choice("LLM_PROVIDER", "openai", {"openai"}))
    model: str = field(default_factory=lambda: env_str("LLM_MODEL", "gpt-4o-mini"))
    temperature: float = field(default_factory=lambda: env_float("LLM_TEMPERATURE", 0.1, min_value=0.0, max_value=2.0))
    max_tokens: int = field(default_factory=lambda: env_int("LLM_MAX_TOKENS", 1024, min_value=1))


@dataclass
class SchemaConfig:
    chunk_size: int = field(default_factory=lambda: env_int("CHUNK_SIZE", 1000, min_value=1))
    chunk_overlap: int = field(default_factory=lambda: env_int("CHUNK_OVERLAP", 100, min_value=0))

    def __post_init__(self) -> None:
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                f"CHUNK_OVERLAP ({self.chunk_overlap}) must be < CHUNK_SIZE ({self.chunk_size})"
            )


@dataclass
class IndexConfig:
    name: str = field(default_factory=lambda: env_str("INDEX_NAME", "chunks"))
    similarity_fn: str = field(
        default_factory=lambda: env_choice("SIMILARITY_FN", "cosine", {"cosine", "euclidean", "dot"})
    )


@dataclass
class PipelineConfig:
    app: AppConfig = field(default_factory=AppConfig)
    neo4j: Neo4jConfig = field(default_factory=Neo4jConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    schema: SchemaConfig = field(default_factory=SchemaConfig)
    index: IndexConfig = field(default_factory=IndexConfig)

    def __post_init__(self) -> None:
        if self.app.app_env != "dev" and not self.neo4j.password:
            raise ValueError("NEO4J_PASSWORD is required when APP_ENV is not dev")

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "app": {"app_env": self.app.app_env},
            "neo4j": {
                "uri": self.neo4j.uri,
                "username": self.neo4j.username,
                "password": "***" if self.neo4j.password else "",
            },
            "embedding": {
                "provider": self.embedding.provider,
                "model": self.embedding.model,
                "st_model": self.embedding.st_model,
                "dimensions": self.embedding.dimensions,
            },
            "llm": {
                "provider": self.llm.provider,
                "model": self.llm.model,
                "temperature": self.llm.temperature,
                "max_tokens": self.llm.max_tokens,
            },
            "schema": {
                "chunk_size": self.schema.chunk_size,
                "chunk_overlap": self.schema.chunk_overlap,
            },
            "index": {
                "name": self.index.name,
                "similarity_fn": self.index.similarity_fn,
            },
        }
```

## Example review comment you can paste on GitHub

> Nice structure overall—using dataclasses plus env defaults keeps config discoverable. I’d suggest tightening validation and secret handling: avoid defaulting `NEO4J_PASSWORD` to `"password"`, add safe parsers for numeric env vars with clear error messages, and enforce invariants (`chunk_overlap < chunk_size`, positive dimensions/tokens, valid `similarity_fn`). This will prevent subtle runtime failures and make deployment behavior safer.
