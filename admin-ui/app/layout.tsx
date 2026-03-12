import "@/app/globals.css";

import type { Metadata } from "next";

import { Providers } from "@/app/providers";
import { env } from "@/lib/config/env";

export const metadata: Metadata = {
  title: env.NEXT_PUBLIC_APP_NAME,
  description: "Enterprise admin console for Uniforma."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
