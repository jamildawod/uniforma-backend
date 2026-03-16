import enum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AttributeType(str, enum.Enum):
    text = "text"
    number = "number"
    select = "select"
    boolean = "boolean"


class Attribute(Base):
    __tablename__ = "attributes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    type: Mapped[AttributeType] = mapped_column(
        Enum(AttributeType, name="attribute_type_enum"),
        nullable=False,
    )

    values: Mapped[list["ProductAttributeValue"]] = relationship(
        back_populates="attribute",
        cascade="all, delete-orphan",
    )
