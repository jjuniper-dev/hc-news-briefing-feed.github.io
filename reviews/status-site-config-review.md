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

## Example review comment you can paste on GitHub

> Nice structure overall—using dataclasses plus env defaults keeps config discoverable. I’d suggest tightening validation and secret handling: avoid defaulting `NEO4J_PASSWORD` to `"password"`, add safe parsers for numeric env vars with clear error messages, and enforce invariants (`chunk_overlap < chunk_size`, positive dimensions/tokens, valid `similarity_fn`). This will prevent subtle runtime failures and make deployment behavior safer.
