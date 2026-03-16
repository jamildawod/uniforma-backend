import { z } from "zod";

const envSchema = z.object({
  NEXT_PUBLIC_APP_NAME: z.string().default("Uniforma Admin"),
  UNIFORMA_API_BASE_URL: z.string().url().default("http://127.0.0.1:9100"),
  UNIFORMA_ADMIN_DEFAULT_ROLE: z.enum(["admin", "editor"]).default("editor")
});

export const env = envSchema.parse({
  NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME,
  UNIFORMA_API_BASE_URL: process.env.UNIFORMA_API_BASE_URL,
  UNIFORMA_ADMIN_DEFAULT_ROLE: process.env.UNIFORMA_ADMIN_DEFAULT_ROLE
});
