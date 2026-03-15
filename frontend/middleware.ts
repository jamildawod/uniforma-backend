import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { AUTH_COOKIE } from "@/lib/auth/cookies";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get(AUTH_COOKIE)?.value;
  const requestHeaders = new Headers(request.headers);

  requestHeaders.set("x-pathname", pathname);

  if (pathname.startsWith("/admin/login")) {
    if (token) {
      return NextResponse.redirect(new URL("/admin/products", request.url));
    }

    return NextResponse.next({
      request: {
        headers: requestHeaders
      }
    });
  }

  if (
    pathname.startsWith("/api/auth") ||
    pathname.startsWith("/_next") ||
    pathname.startsWith("/static") ||
    pathname.startsWith("/assets")
  ) {
    return NextResponse.next({
      request: {
        headers: requestHeaders
      }
    });
  }

  if (pathname.startsWith("/admin") && !token) {
    return NextResponse.redirect(new URL("/admin/login", request.url));
  }

  return NextResponse.next({
    request: {
      headers: requestHeaders
    }
  });
}

export const config = {
  matcher: ["/admin/:path*"]
};
