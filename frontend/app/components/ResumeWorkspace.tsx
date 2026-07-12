"use client";

import { useState } from "react";
import ResumeForm from "./ResumeForm";
import AnalyzeForm from "./AnalyzeForm";
import type { ResumeSummary } from "@/app/lib/types";

// Picks which of the user's resumes to analyze against, and offers a way to
// upload another one. The resume list itself is server-fetched (in page.tsx)
// and passed down — this component only tracks which one is selected.
export default function ResumeWorkspace({
  resumes,
}: {
  resumes: ResumeSummary[];
}) {
  const [selectedId, setSelectedId] = useState<number | null>(
    resumes[0]?.id ?? null,
  );
  const [showUpload, setShowUpload] = useState(false);

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-border bg-card p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-base font-semibold">Your resumes</h2>
          <button
            type="button"
            onClick={() => setShowUpload((v) => !v)}
            className="text-sm font-medium text-brand hover:underline"
          >
            {showUpload ? "Cancel" : "Upload a new resume"}
          </button>
        </div>

        {showUpload ? (
          <ResumeForm onUploaded={() => setShowUpload(false)} />
        ) : (
          <div className="space-y-2">
            {resumes.map((resume) => (
              <label
                key={resume.id}
                className={`flex cursor-pointer items-center gap-3 rounded-lg border px-3 py-2 text-sm transition ${
                  selectedId === resume.id
                    ? "border-brand bg-brand/5"
                    : "border-border"
                }`}
              >
                <input
                  type="radio"
                  name="resume"
                  checked={selectedId === resume.id}
                  onChange={() => setSelectedId(resume.id)}
                  className="accent-brand"
                />
                <span className="flex-1 truncate">{resume.preview}</span>
                <span className="shrink-0 text-xs text-muted">
                  {new Date(resume.created_at).toLocaleDateString("en-US", {
                    timeZone: "UTC",
                  })}
                </span>
              </label>
            ))}
          </div>
        )}
      </section>

      <AnalyzeForm resumeId={selectedId} />
    </div>
  );
}
