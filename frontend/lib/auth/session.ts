import { cookies } from "next/headers";
import { decodeJwt } from "jose";

import { env } from "@/lib/config/env";
import { AUTH_COOKIE, ROLE_COOKIE } from "@/lib/auth/cookies";
import type { SessionState, UserRole } from "@/lib/types/auth";

export async function getSession(): Promise<SessionState> {
  const cookieStore = cookies();
  const token = cookieStore.get(AUTH_COOKIE)?.value;
  const roleCookie = cookieStore.get(ROLE_COOKIE)?.value as UserRole | undefined;

  if (!token) {
    return {
      isAuthenticated: false,
      user: null
    };
  }

  try {
    const payload = decodeJwt(token);
    const subject = typeof payload.sub === "string" ? payload.sub : null;
    const payloadRole = typeof payload.role === "string" ? payload.role : undefined;
    const role = normalizeRole(roleCookie ?? payloadRole ?? env.UNIFORMA_ADMIN_DEFAULT_ROLE);
    return {
      isAuthenticated: true,
      user: {
        email: subject,
        role
      }
    };
  } catch {
    return {
      isAuthenticated: false,
      user: null
    };
  }
}

function normalizeRole(value: string): UserRole {
  return value === "admin" ? "admin" : "editor";
}
