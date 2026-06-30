import type { AnalysisResult } from "@/app/lib/types";
import ScoreRing from "./ScoreRing";

function SkillChips({
  title,
  skills,
  variant,
}: {
  title: string;
  skills: string[];
  variant: "matched" | "missing";
}) {
  const styles =
    variant === "matched"
      ? "border-success/30 bg-success/10 text-success"
      : "border-danger/30 bg-danger/10 text-danger";

  return (
    <div>
      <h4 className="mb-2 text-sm font-semibold">
        {title}{" "}
        <span className="font-normal text-muted">({skills.length})</span>
      </h4>
      {skills.length === 0 ? (
        <p className="text-sm text-muted">None</p>
      ) : (
        <ul className="flex flex-wrap gap-2">
          {skills.map((skill) => (
            <li
              key={skill}
              className={`rounded-full border px-3 py-1 text-xs font-medium ${styles}`}
            >
              {skill}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function AnalysisResultView({
  result,
}: {
  result: AnalysisResult;
}) {
  return (
    <div className="space-y-6 rounded-xl border border-border bg-card p-6 shadow-sm">
      <div className="flex flex-col items-center gap-5 sm:flex-row sm:items-center">
        <ScoreRing score={result.match_score} />
        <div className="space-y-1 text-center sm:text-left">
          <h3 className="text-lg font-bold">Match Analysis</h3>
          <p className="text-sm text-muted">
            How well your resume fits this role, based on the skills it surfaces.
          </p>
        </div>
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <SkillChips
          title="Matched skills"
          skills={result.matched_skills}
          variant="matched"
        />
        <SkillChips
          title="Missing skills"
          skills={result.missing_skills}
          variant="missing"
        />
      </div>

      <div className="rounded-lg border border-border bg-background/50 p-4">
        <h4 className="mb-1 text-sm font-semibold">Positioning advice</h4>
        <p className="text-sm leading-relaxed text-foreground/80">
          {result.positioning_advice}
        </p>
      </div>
    </div>
  );
}
