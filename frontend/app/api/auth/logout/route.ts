import { NextResponse } from "next/server";

import { AUTH_COOKIE, REFRESH_COOKIE, ROLE_COOKIE } from "@/lib/auth/cookies";

export async function POST() {
  const response = NextResponse.redirect(new URL("/admin/login", "http://localhost"));
  response.cookies.delete(AUTH_COOKIE);
  response.cookies.delete(REFRESH_COOKIE);
  response.cookies.delete(ROLE_COOKIE);
  return response;
}
