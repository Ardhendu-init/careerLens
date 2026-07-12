import { createBrowserClient } from "@supabase/ssr";

// Supabase client for Client Components. The session itself lives in
// httpOnly cookies managed by @supabase/ssr — this client never handles the
// JWT directly on the browser.
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  );
}
