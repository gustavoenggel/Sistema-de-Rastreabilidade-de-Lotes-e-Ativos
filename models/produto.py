import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, String, Boolean, Integer, Numeric, Enum as SQLEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Database.conexao import Base
from Models.enum import UnidadeMedida

if TYPE_CHECKING:
    from Models.lote import Lote


class Produto(Base):
    __tablename__ = "produtos"

    # Chave Primária UUID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Código SKU (Stock Keeping Unit) - ex: "MAT-PP-001"
    sku: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    # Nome comercial/técnico - ex: "Resina Polipropileno PP-020"
    nome: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Unidade de medida padronizada (KG, UN, L, etc.)
    unidade_medida: Mapped[UnidadeMedida] = mapped_column(
        SQLEnum(UnidadeMedida, name="unidade_medida_enum"),
        default=UnidadeMedida.QUILOGRAMA,
        nullable=False,
    )

    # Prazo de Validade em dias (Base para calcular a data_validade na criação do lote)
    dias_validade: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # Estoque Mínimo de Segurança
    estoque_minimo: Mapped[Optional[float]] = mapped_column(
        Numeric(15, 4),
        default=0.0,
        nullable=True,
    )

    # Status do produto no catálogo
    ativo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Timestamps
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relacionamento 1-para-Muitos com Lotes
    lotes: Mapped[List["Lote"]] = relationship(
        "Lote",
        back_populates="produto",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Produto(sku='{self.sku}', nome='{self.nome}', unidade='{self.unidade_medida.value}')>"