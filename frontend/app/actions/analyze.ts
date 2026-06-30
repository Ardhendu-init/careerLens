"use server";

import { apiPost } from "@/app/lib/api";
import type { ActionState, AnalysisResult } from "@/app/lib/types";

export async function analyzeResume(
  resumeId: number | null,
  _prevState: ActionState<AnalysisResult>,
  formData: FormData,
): Promise<ActionState<AnalysisResult>> {
  const jdText = (formData.get("jd-text") as string)?.trim();

  if (!jdText) {
    return {
      status: "error",
      message: "Paste a job description to analyze against.",
    };
  }
  if (!resumeId) {
    return {
      status: "error",
      message: "Upload your resume first.",
    };
  }

  try {
    const data = await apiPost<AnalysisResult>("/analyze/", {
      jd_text: jdText,
      resume_id: resumeId,
    });
    return { status: "success", message: "Analysis complete.", data };
  } catch (error) {
    return {
      status: "error",
      message: error instanceof Error ? error.message : "Something went wrong.",
    };
  }
}
