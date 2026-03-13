export const apiEndpoints = {
  login: "/api/v1/auth/login",
  adminProducts: "/api/v1/admin/products",
  adminProduct: (id: string) => `/api/v1/admin/products/${id}`,
  adminProductPublish: (id: string) => `/api/v1/admin/products/${id}/publish`,
  adminProductImage: (id: string) => `/api/v1/admin/products/${id}/image`,
  adminUpload: "/api/v1/admin/upload",
  adminQuotes: "/api/v1/admin/quotes",
  adminIntelligenceSummary: "/api/v1/admin/intelligence/summary",
  adminIntelligenceDataQuality: "/api/v1/admin/intelligence/data-quality",
  adminIntelligenceSyncHealth: "/api/v1/admin/intelligence/sync-health",
  adminIntelligenceOverrideConflicts: "/api/v1/admin/intelligence/override-conflicts",
  adminSyncTrigger: "/api/v1/admin/sync/pim",
  adminSyncRuns: "/api/v1/admin/sync/runs",
  quotes: "/api/v1/quotes",
  publicProducts: "/api/v1/products",
  publicProduct: (slug: string) => `/api/v1/products/${slug}`
} as const;
