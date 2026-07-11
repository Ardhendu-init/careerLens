import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

// Supabase client for Server Components and Server Actions. Reads/writes the
// session via the request's cookies. `setAll` can fail when called from a
// Server Component (cookies are read-only there) — that's expected, the
// proxy (frontend/proxy.ts) is responsible for refreshing the session cookie
// in that case.
export async function createClient() {
  const cookieStore = await cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options),
            );
          } catch {
            // Called from a Server Component — ignore, proxy handles refresh.
          }
        },
      },
    },
  );
}

/**
 * Access token for the current request, to forward to FastAPI as
 * `Authorization: Bearer <token>`. Read from cookies only — never used for
 * an authorization decision here, since only FastAPI verifies the JWT.
 */
export async function getAccessToken(): Promise<string | null> {
  const supabase = await createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return session?.access_token ?? null;
}
