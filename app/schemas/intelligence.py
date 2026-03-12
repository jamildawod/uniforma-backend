from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


HealthStatus = Literal["healthy", "warning", "critical", "unavailable"]


class SystemHealthResponse(BaseModel):
    status: HealthStatus
    generated_at: datetime
    total_products: int = 0
    active_products: int = 0
    deleted_products: int = 0
    total_variants: int = 0
    last_successful_sync_at: datetime | None = None
    running_syncs: int = 0
    override_count: int = 0


class DataQualityMetric(BaseModel):
    key: str
    label: str
    count: int
    description: str
    filter: str
    severity: HealthStatus


class DataQualityResponse(BaseModel):
    status: HealthStatus
    generated_at: datetime
    metrics: list[DataQualityMetric] = Field(default_factory=list)


class SyncRun(BaseModel):
    id: int
    started_at: datetime
    finished_at: datetime | None = None
    status: Literal["success", "failed", "running"]
    duration_seconds: float | None = None
    products_created: int = 0
    products_updated: int = 0
    variants_created: int = 0
    variants_updated: int = 0
    images_synced: int = 0
    error_message: str | None = None


class SyncHealthResponse(BaseModel):
    status: HealthStatus
    generated_at: datetime
    running_syncs: int = 0
    last_successful_sync_at: datetime | None = None
    failed_runs_last_24h: int = 0
    average_duration_seconds: float | None = None
    last_failed_sync_at: datetime | None = None
    soft_deleted_products_last_run: int = 0
    soft_deleted_variants_last_run: int = 0
    page: int = 1
    page_size: int = 10
    total: int = 0
    recent_runs: list[SyncRun] = Field(default_factory=list)


class OverrideConflict(BaseModel):
    id: str
    product_id: str
    product_name: str
    field_name: str
    source_value: str | None = None
    override_value: str | None = None
    final_value: str | None = None
    severity: HealthStatus
    updated_at: datetime


class OverrideConflictResponse(BaseModel):
    status: HealthStatus
    generated_at: datetime
    page: int = 1
    page_size: int = 10
    total: int = 0
    conflicts: list[OverrideConflict] = Field(default_factory=list)
