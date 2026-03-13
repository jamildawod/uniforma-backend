from app.repositories.product_repository import ProductRepository
from app.schemas.product import DataQualityIssue, DataQualityResponse


class DataQualityService:
    def __init__(self, repository: ProductRepository) -> None:
        self.repository = repository

    async def get_issues(self) -> DataQualityResponse:
        products = await self.repository.list_products(limit=500, offset=0)
        missing_brand = 0
        missing_description = 0
        missing_image = 0
        missing_ean = 0

        for product in products:
            if product.brand_id is None and not (product.brand or "").strip():
                missing_brand += 1
            if not (product.description or "").strip():
                missing_description += 1
            if not product.images:
                missing_image += 1
            if any(not (variant.ean or "").strip() for variant in product.variants):
                missing_ean += 1

        return DataQualityResponse(
            issues=[
                DataQualityIssue(key="missing_brand", label="Missing brand", count=missing_brand),
                DataQualityIssue(key="missing_description", label="Missing description", count=missing_description),
                DataQualityIssue(key="missing_image", label="Missing image", count=missing_image),
                DataQualityIssue(key="missing_ean", label="Missing EAN", count=missing_ean),
            ]
        )
