import { decodeJwt } from "jose";
import { NextResponse } from "next/server";

import { AUTH_COOKIE, REFRESH_COOKIE, ROLE_COOKIE } from "@/lib/auth/cookies";
import { env } from "@/lib/config/env";
import { apiEndpoints } from "@/lib/api/endpoints";
import type { AuthTokens } from "@/lib/types/auth";

export async function POST(request: Request) {
  const payload = await readLoginPayload(request);
  const form = new URLSearchParams({
    username: payload.username,
    password: payload.password
  });

  const response = await fetch(`${env.UNIFORMA_API_BASE_URL}${apiEndpoints.login}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: form.toString(),
    cache: "no-store"
  });

  const body = (await response.json()) as AuthTokens | { detail?: string };
  if (!response.ok) {
    return NextResponse.json({ detail: (body as { detail?: string }).detail ?? "Login failed" }, { status: response.status });
  }

  const tokens = body as AuthTokens;
  const nextResponse = NextResponse.json(tokens);
  const payloadData = safeDecode(tokens.access_token);
  const role = payloadData?.role === "admin" ? "admin" : env.UNIFORMA_ADMIN_DEFAULT_ROLE;

  nextResponse.cookies.set(AUTH_COOKIE, tokens.access_token, {
    httpOnly: true,
    sameSite: "lax",
    secure: true,
    path: "/"
  });
  nextResponse.cookies.set(REFRESH_COOKIE, tokens.refresh_token, {
    httpOnly: true,
    sameSite: "lax",
    secure: true,
    path: "/"
  });
  nextResponse.cookies.set(ROLE_COOKIE, role, {
    httpOnly: false,
    sameSite: "lax",
    secure: true,
    path: "/"
  });

  return nextResponse;
}

async function readLoginPayload(request: Request): Promise<{ username: string; password: string }> {
  const contentType = request.headers.get("content-type") ?? "";
  if (contentType.includes("application/x-www-form-urlencoded")) {
    const formData = await request.formData();
    return {
      username: String(formData.get("username") ?? ""),
      password: String(formData.get("password") ?? "")
    };
  }

  const payload = (await request.json()) as { email?: string; username?: string; password?: string };
  return {
    username: payload.username ?? payload.email ?? "",
    password: payload.password ?? ""
  };
}

function safeDecode(token: string): { role?: string } | null {
  try {
    const payload = decodeJwt(token);
    return {
      role: typeof payload.role === "string" ? payload.role : undefined
    };
  } catch {
    return null;
  }
}
