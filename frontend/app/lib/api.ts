// Base URL for the FastAPI backend. Override with NEXT_PUBLIC_API_URL in .env.local.
export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    // FastAPI sends errors as { detail: "..." }
    const detail = await res
      .json()
      .then((d) => d?.detail as string | undefined)
      .catch(() => undefined);
    throw new Error(detail ?? `Request failed (${res.status})`);
  }

  return res.json() as Promise<T>;
}

function authHeaders(token?: string | null): HeadersInit {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * Thin wrapper around fetch for talking to the backend. Throws an Error with a
 * useful message when the response is not ok so server actions can catch it.
 */
export async function apiPost<T>(
  path: string,
  body: unknown,
  token?: string | null,
): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify(body),
    cache: "no-store",
  });

  return handleResponse<T>(res);
}

export async function apiGet<T>(path: string, token?: string | null): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: authHeaders(token),
    cache: "no-store",
  });

  return handleResponse<T>(res);
}
