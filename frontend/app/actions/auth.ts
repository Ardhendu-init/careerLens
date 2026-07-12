"use server";

import { redirect } from "next/navigation";
import { createClient } from "@/app/lib/supabase/server";
import type { ActionState } from "@/app/lib/types";

export async function login(
  _prevState: ActionState<never>,
  formData: FormData,
): Promise<ActionState<never>> {
  const email = (formData.get("email") as string)?.trim();
  const password = formData.get("password") as string;

  if (!email || !password) {
    return { status: "error", message: "Enter your email and password." };
  }

  const supabase = await createClient();
  const { error } = await supabase.auth.signInWithPassword({ email, password });

  if (error) {
    return { status: "error", message: error.message };
  }

  redirect("/");
}

export async function signup(
  _prevState: ActionState<never>,
  formData: FormData,
): Promise<ActionState<never>> {
  const email = (formData.get("email") as string)?.trim();
  const password = formData.get("password") as string;

  if (!email || !password) {
    return { status: "error", message: "Enter your email and password." };
  }
  if (password.length < 8) {
    return {
      status: "error",
      message: "Password must be at least 8 characters.",
    };
  }

  const supabase = await createClient();
  const { data, error } = await supabase.auth.signUp({ email, password });

  if (error) {
    return { status: "error", message: error.message };
  }

  if (!data.session) {
    // Email confirmation is required before a session is issued.
    return {
      status: "success",
      message: "Check your email to confirm your account, then log in.",
    };
  }

  redirect("/");
}

export async function logout() {
  const supabase = await createClient();
  await supabase.auth.signOut();
  redirect("/login");
}
