"use server";

import { apiPost } from "@/app/lib/api";
import type { ActionState } from "@/app/lib/types";

type UploadResponse = {
  message: string;
  resume_id: number;
  chunks: number;
};

export async function uploadResume(
  _prevState: ActionState<UploadResponse>,
  formData: FormData,
): Promise<ActionState<UploadResponse>> {
  const text = (formData.get("resume-text") as string)?.trim();

  if (!text) {
    return { status: "error", message: "Please paste your resume text first." };
  }

  try {
    const data = await apiPost<UploadResponse>("/resume/", { text });
    return {
      status: "success",
      message: `Resume saved — indexed into ${data.chunks} chunk${
        data.chunks === 1 ? "" : "s"
      }.`,
      data,
    };
  } catch (error) {
    return {
      status: "error",
      message: error instanceof Error ? error.message : "Something went wrong.",
    };
  }
}
