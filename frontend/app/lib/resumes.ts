import "server-only";

import { apiGet } from "@/app/lib/api";
import { getAccessToken } from "@/app/lib/supabase/server";
import type { ResumeSummary } from "@/app/lib/types";

// Server-only: the caller's own resumes, newest first. Empty for a signed-out
// request rather than throwing, since the proxy already gates unauthenticated
// access to this page.
export async function getMyResumes(): Promise<ResumeSummary[]> {
  const token = await getAccessToken();
  if (!token) return [];
  return apiGet<ResumeSummary[]>("/resume/", token);
}
