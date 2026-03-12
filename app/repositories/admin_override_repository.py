import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_override import AdminOverride


class AdminOverrideRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_product_ids(
        self,
        product_ids: list[uuid.UUID],
    ) -> dict[uuid.UUID, list[AdminOverride]]:
        if not product_ids:
            return {}

        statement = select(AdminOverride).where(AdminOverride.product_id.in_(product_ids))
        result = await self.session.execute(statement)
        overrides = result.scalars().all()

        grouped: dict[uuid.UUID, list[AdminOverride]] = {product_id: [] for product_id in product_ids}
        for override in overrides:
            grouped.setdefault(override.product_id, []).append(override)
        return grouped

    async def get_by_product_and_field(
        self,
        product_id: uuid.UUID,
        field_name: str,
    ) -> AdminOverride | None:
        statement = select(AdminOverride).where(
            AdminOverride.product_id == product_id,
            AdminOverride.field_name == field_name,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def add(self, override: AdminOverride) -> AdminOverride:
        self.session.add(override)
        await self.session.flush()
        return override
