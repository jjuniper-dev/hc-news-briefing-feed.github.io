import fs from "fs";
import path from "path";
import Ajv2020 from "ajv/dist/2020";

export type GateResult = "Pass" | "Fail" | "N/A";
export type RagStatus = "Green" | "Amber" | "Red";

export interface AssessmentData {
  vendor: string;
  version: string;
  review_date: string;
  item_type: string;
  capability_type: string;
  tier: string;
  gates: Record<string, GateResult>;
  scores: {
    governance: number;
    architecture: number;
    capability: number;
    procurement: number;
    composite: number;
  };
  positioning: {
    openness: string;
    sovereignty: string;
    runtime: string;
  };
  recommendation: string;
  metadata?: {
    reviewer?: string;
    status?: string;
    latest?: boolean;
  };
}

export interface AssessmentMeta {
  vendor: string;
  version: string;
  latest?: boolean;
  reviewer?: string;
  status?: string;
}

export interface AssessmentBundle {
  vendor: string;
  version: string;
  data: AssessmentData;
  markdown: string;
  meta: AssessmentMeta;
}

export interface AssessmentIndexEntry {
  vendor: string;
  version: string;
  composite: number;
  rag: RagStatus;
  recommendation: string;
}

export function loadAssessments(contentRoot = path.join(process.cwd(), "content/assessments")) {
  const schemaPath = path.join(process.cwd(), "schemas/assessment.schema.json");
  const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));

  const ajv = new Ajv2020({ allErrors: true, strict: false });
  const validate = ajv.compile<AssessmentData>(schema);

  const byVendor: Record<string, AssessmentBundle[]> = {};
  const index: AssessmentIndexEntry[] = [];

  if (!fs.existsSync(contentRoot)) {
    return { index, byVendor };
  }

  for (const vendor of fs.readdirSync(contentRoot)) {
    const vendorDir = path.join(contentRoot, vendor);
    if (!fs.statSync(vendorDir).isDirectory()) continue;

    const bundles: AssessmentBundle[] = [];

    for (const version of fs.readdirSync(vendorDir)) {
      const versionDir = path.join(vendorDir, version);
      if (!fs.statSync(versionDir).isDirectory()) continue;

      const data = JSON.parse(
        fs.readFileSync(path.join(versionDir, "assessment.json"), "utf8")
      ) as AssessmentData;
      const markdown = fs.readFileSync(path.join(versionDir, "assessment.md"), "utf8");
      const meta = JSON.parse(
        fs.readFileSync(path.join(versionDir, "meta.json"), "utf8")
      ) as AssessmentMeta;

      if (!validate(data)) {
        throw new Error(
          `Assessment validation failed for ${vendor}/${version}: ${JSON.stringify(validate.errors)}`
        );
      }

      const bundle: AssessmentBundle = {
        vendor,
        version,
        data,
        markdown,
        meta
      };

      bundles.push(bundle);

      if (meta.latest) {
        index.push({
          vendor,
          version,
          composite: data.scores.composite,
          rag: computeRag(data),
          recommendation: data.recommendation
        });
      }
    }

    bundles.sort((a, b) => a.version.localeCompare(b.version, undefined, { numeric: true }));
    byVendor[vendor] = bundles;
  }

  index.sort((a, b) => a.vendor.localeCompare(b.vendor));
  return { index, byVendor };
}

export function computeRag(assessment: AssessmentData): RagStatus {
  if (Object.values(assessment.gates).includes("Fail")) return "Red";

  const score = assessment.scores.composite;
  if (score >= 70) return "Green";
  if (score >= 50) return "Amber";
  return "Red";
}
