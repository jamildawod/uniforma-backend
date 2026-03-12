from pydantic import BaseModel


class PimSyncResponse(BaseModel):
    products_created: int = 0
    products_updated: int = 0
    products_unchanged: int = 0
    variants_created: int = 0
    variants_updated: int = 0
    variants_unchanged: int = 0
    images_discovered: int = 0
    images_synced: int = 0
