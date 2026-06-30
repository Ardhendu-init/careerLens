"use client";

import { useActionState } from "react";
import { analyzeResume } from "@/app/actions/analyze";
import type { ActionState, AnalysisResult } from "@/app/lib/types";
import SubmitButton from "./SubmitButton";
import StatusBanner from "./StatusBanner";
import AnalysisResultView from "./AnalysisResultView";

const initialState: ActionState<AnalysisResult> = {
  status: "idle",
  message: "",
};

export default function AnalyzeForm({ resumeId }: { resumeId: number | null }) {
  const [state, formAction] = useActionState(
    analyzeResume.bind(null, resumeId),
    initialState,
  );

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-border bg-card p-6 shadow-sm">
        <div className="mb-4 flex items-center gap-2">
          <span className="flex size-6 items-center justify-center rounded-full bg-brand text-xs font-bold text-brand-fg">
            2
          </span>
          <h2 className="text-base font-semibold">Paste a job description</h2>
        </div>

        {resumeId === null ? (
          <p className="text-sm text-muted">
            Upload your resume first to analyze it against a job description.
          </p>
        ) : (
          <form action={formAction} className="space-y-3">
            <textarea
              name="jd-text"
              required
              rows={8}
              placeholder="Paste the job description you're targeting…"
              className="w-full resize-y rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none placeholder:text-muted focus-visible:border-brand focus-visible:ring-2 focus-visible:ring-brand/30"
            />
            <div className="flex items-center justify-between gap-3">
              {/* Only surface errors here; success renders as the result card below. */}
              <StatusBanner
                status={state.status === "error" ? "error" : "idle"}
                message={state.status === "error" ? state.message : ""}
              />
              <div className="ml-auto">
                <SubmitButton pendingLabel="Analyzing…">
                  Analyze fit
                </SubmitButton>
              </div>
            </div>
          </form>
        )}
      </section>

      {state.status === "success" && state.data && (
        <AnalysisResultView result={state.data} />
      )}
    </div>
  );
}
