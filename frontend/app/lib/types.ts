export type AnalysisResult = {
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  positioning_advice: string;
};

// Shared shape returned by the resume/analyze server actions to the client.
export type ActionState<T> = {
  status: "idle" | "success" | "error";
  message: string;
  data?: T;
};
