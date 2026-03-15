import { z } from "zod";

export const overrideFieldsSchema = z.object({
  name: z.string().trim().min(1).max(255).optional().or(z.literal("")),
  description: z.string().trim().max(4000).optional().or(z.literal("")),
  brand: z.string().trim().max(255).optional().or(z.literal(""))
});

export type OverrideFieldsInput = z.infer<typeof overrideFieldsSchema>;

export const imageSchema = z.object({
  url: z.string().min(1).max(1024),
  variant_id: z.coerce.number().int().optional().nullable(),
  is_primary: z.boolean().default(false),
  position: z.coerce.number().int().min(0).default(0)
});

export type ImageInput = z.infer<typeof imageSchema>;
