import "@/app/globals.css";

import type { Metadata } from "next";

import { Providers } from "@/app/providers";
import { env } from "@/lib/config/env";

export const metadata: Metadata = {
  title: "UNIFORMA",
  description: "UNIFORMA erbjuder profilprodukter, arbetsklader och tryck for foretag."
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
