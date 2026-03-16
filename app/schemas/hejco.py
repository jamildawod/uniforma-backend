from pydantic import BaseModel


class HejcoImportResponse(BaseModel):
    products_imported: int = 0
    products_updated: int = 0
    images_matched: int = 0
    stock_updated: int = 0
    variants_imported: int = 0
    variants_updated: int = 0
