"use client";

import { useActionState } from "react";
import Link from "next/link";
import { signup } from "@/app/actions/auth";
import type { ActionState } from "@/app/lib/types";
import SubmitButton from "@/app/components/SubmitButton";
import StatusBanner from "@/app/components/StatusBanner";

const initialState: ActionState<never> = { status: "idle", message: "" };

export default function SignupForm() {
  const [state, formAction] = useActionState(signup, initialState);

  return (
    <>
      <form action={formAction} className="space-y-3">
        <input
          name="email"
          type="email"
          required
          placeholder="Email"
          className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none placeholder:text-muted focus-visible:border-brand focus-visible:ring-2 focus-visible:ring-brand/30"
        />
        <input
          name="password"
          type="password"
          required
          minLength={8}
          placeholder="Password (min. 8 characters)"
          className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none placeholder:text-muted focus-visible:border-brand focus-visible:ring-2 focus-visible:ring-brand/30"
        />
        <StatusBanner status={state.status} message={state.message} />
        <SubmitButton pendingLabel="Signing up…">Sign up</SubmitButton>
      </form>
      <p className="mt-4 text-center text-sm text-muted">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-brand hover:underline">
          Log in
        </Link>
      </p>
    </>
  );
}
