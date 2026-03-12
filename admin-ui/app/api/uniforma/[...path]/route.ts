import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE } from "@/lib/auth/cookies";
import { env } from "@/lib/config/env";

type Context = {
  params: {
    path: string[];
  };
};

export async function GET(request: Request, context: Context) {
  return proxyRequest(request, context);
}

export async function POST(request: Request, context: Context) {
  return proxyRequest(request, context);
}

export async function PATCH(request: Request, context: Context) {
  return proxyRequest(request, context);
}

async function proxyRequest(request: Request, context: Context) {
  const token = cookies().get(AUTH_COOKIE)?.value;
  const path = context.params.path.join("/");
  const url = new URL(request.url);
  const upstreamUrl = `${env.UNIFORMA_API_BASE_URL}/${path}${url.search}`;

  const upstreamResponse = await fetch(upstreamUrl, {
    method: request.method,
    headers: {
      "Content-Type": request.headers.get("content-type") ?? "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: request.method === "GET" ? undefined : await request.text(),
    cache: "no-store"
  });

  const text = await upstreamResponse.text();
  return new NextResponse(text, {
    status: upstreamResponse.status,
    headers: {
      "Content-Type": upstreamResponse.headers.get("content-type") ?? "application/json"
    }
  });
}
