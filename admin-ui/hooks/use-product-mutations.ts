"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createProductImage, patchProductOverride, triggerPimSync } from "@/lib/api/client";
import type { AdminImagePayload, AdminOverridePayload, AdminProduct } from "@/lib/types/products";

export function usePatchProductOverride(productId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: AdminOverridePayload) => patchProductOverride(productId, payload),
    onMutate: async (payload) => {
      const key = ["admin-product", productId] as const;
      await queryClient.cancelQueries({ queryKey: key });
      const previous = queryClient.getQueryData<AdminProduct>(key);
      if (previous) {
        queryClient.setQueryData<AdminProduct>(key, {
          ...previous,
          applied_overrides: {
            ...previous.applied_overrides,
            ...payload.overrides
          }
        });
      }
      return { previous };
    },
    onError: (_error, _payload, context) => {
      if (context?.previous) {
        queryClient.setQueryData(["admin-product", productId], context.previous);
      }
    },
    onSuccess: (next) => {
      queryClient.setQueryData(["admin-product", productId], next);
      queryClient.invalidateQueries({ queryKey: ["admin-products"] });
    }
  });
}

export function useCreateProductImage(productId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: AdminImagePayload) => createProductImage(productId, payload),
    onSuccess: (next) => {
      queryClient.setQueryData(["admin-product", productId], next);
      queryClient.invalidateQueries({ queryKey: ["admin-products"] });
    }
  });
}

export function useTriggerSync() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => triggerPimSync(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sync-runs"] });
      queryClient.invalidateQueries({ queryKey: ["admin-products"] });
    }
  });
}
