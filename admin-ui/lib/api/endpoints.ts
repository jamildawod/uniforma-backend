export const apiEndpoints = {
  login: "/api/v1/auth/login",
  adminProducts: "/api/v1/admin/products",
  adminProduct: (id: string) => `/api/v1/admin/products/${id}`,
  adminProductImage: (id: string) => `/api/v1/admin/products/${id}/image`,
  adminIntelligenceSummary: "/api/v1/admin/intelligence/summary",
  adminIntelligenceDataQuality: "/api/v1/admin/intelligence/data-quality",
  adminIntelligenceSyncHealth: "/api/v1/admin/intelligence/sync-health",
  adminIntelligenceOverrideConflicts: "/api/v1/admin/intelligence/override-conflicts",
  adminSyncTrigger: "/api/v1/admin/sync/pim",
  adminSyncRuns: "/api/v1/admin/sync/runs",
  publicProducts: "/api/v1/products",
  publicProduct: (slug: string) => `/api/v1/products/${slug}`
} as const;
