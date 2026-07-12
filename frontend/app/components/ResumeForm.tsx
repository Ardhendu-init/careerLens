"use client";

import { useActionState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { uploadResume } from "@/app/actions/resume";
import type { ActionState } from "@/app/lib/types";
import SubmitButton from "./SubmitButton";
import StatusBanner from "./StatusBanner";

const initialState: ActionState<never> = { status: "idle", message: "" };

export default function ResumeForm({ onUploaded }: { onUploaded?: () => void }) {
  const [state, formAction] = useActionState(uploadResume, initialState);
  const router = useRouter();

  useEffect(() => {
    if (state.status === "success") {
      // The resume list lives in the parent Server Component — refresh it
      // so the new resume shows up instead of tracking an id in client state.
      router.refresh();
      onUploaded?.();
    }
  }, [state, router, onUploaded]);

  return (
    <section className="rounded-xl border border-border bg-card p-6 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <span className="flex size-6 items-center justify-center rounded-full bg-brand text-xs font-bold text-brand-fg">
          1
        </span>
        <h2 className="text-base font-semibold">Paste your resume</h2>
      </div>

      <form action={formAction} className="space-y-3">
        <textarea
          name="resume-text"
          required
          rows={8}
          placeholder="Paste the full text of your resume here…"
          className="w-full resize-y rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none placeholder:text-muted focus-visible:border-brand focus-visible:ring-2 focus-visible:ring-brand/30"
        />
        <div className="flex items-center justify-between gap-3">
          <StatusBanner status={state.status} message={state.message} />
          <div className="ml-auto">
            <SubmitButton pendingLabel="Saving…">Save resume</SubmitButton>
          </div>
        </div>
      </form>
    </section>
  );
}
