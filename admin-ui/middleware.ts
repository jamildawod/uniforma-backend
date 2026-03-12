import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { AUTH_COOKIE } from "@/lib/auth/cookies";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get(AUTH_COOKIE)?.value;

  if (pathname.startsWith("/admin/login") && token) {
    return NextResponse.redirect(new URL("/admin/products", request.url));
  }

  if (pathname.startsWith("/admin") && !pathname.startsWith("/admin/login") && !token) {
    return NextResponse.redirect(new URL("/admin/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*"]
};
