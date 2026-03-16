import "@/app/globals.css";

import type { Metadata } from "next";

import { Providers } from "@/app/providers";
import { env } from "@/lib/config/env";

export const metadata: Metadata = {
  title: {
    default: "Uniforma",
    template: "%s"
  },
  description: "UNIFORMA erbjuder profilprodukter, arbetsklader och tryck for foretag.",
  openGraph: {
    title: "Uniforma",
    description: "UNIFORMA erbjuder profilprodukter, arbetsklader och tryck for foretag.",
    type: "website"
  }
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="sv">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
