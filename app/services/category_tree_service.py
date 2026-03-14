from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.text import slugify
from app.models.category import Category
from app.schemas.product import CategoryTreeNode


CATEGORY_TREE = {
    "Dental": ["Byxor", "Tunikor", "Rockar", "Jackor", "Accessoarer"],
    "Djursjukvård": ["Byxor", "Tunikor", "Rockar", "Jackor", "Accessoarer"],
    "Vård & Omsorg": ["Byxor", "Tunikor", "Rockar", "Jackor", "Accessoarer"],
    "Städ & Service": ["Byxor", "Tunikor", "Rockar", "Jackor", "Accessoarer"],
    "Kök": ["Byxor", "Tunikor", "Rockar", "Jackor", "Accessoarer"],
    "Skönhet & Hälsa": ["Byxor", "Tunikor", "Rockar", "Jackor", "Accessoarer"],
}


class CategoryTreeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def ensure_default_tree(self) -> None:
        result = await self.session.execute(select(Category))
        by_slug = {category.slug: category for category in result.scalars().all()}
        created = False
        for root_name, children in CATEGORY_TREE.items():
            root_slug = slugify(root_name)
            root = by_slug.get(root_slug)
            if root is None:
                root = Category(name=root_name, slug=root_slug)
                self.session.add(root)
                await self.session.flush()
                by_slug[root_slug] = root
                created = True
            for child_name in children:
                child_slug = slugify(f"{root_name}-{child_name}")
                if child_slug in by_slug:
                    continue
                child = Category(name=child_name, slug=child_slug, parent_id=root.id)
                self.session.add(child)
                await self.session.flush()
                by_slug[child_slug] = child
                created = True
        if created:
            await self.session.commit()

    async def build_tree(self) -> list[CategoryTreeNode]:
        result = await self.session.execute(select(Category).order_by(Category.position.asc(), Category.name.asc()))
        categories = list(result.scalars().all())
        children_by_parent: dict[int | None, list[Category]] = {}
        for category in categories:
            children_by_parent.setdefault(category.parent_id, []).append(category)

        def build_node(category: Category) -> CategoryTreeNode:
            return CategoryTreeNode(
                id=category.id,
                name=category.name,
                slug=category.slug,
                children=[build_node(child) for child in children_by_parent.get(category.id, [])],
            )

        return [build_node(category) for category in children_by_parent.get(None, [])]
