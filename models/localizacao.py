import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, String, Boolean, Enum as SQLEnum, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.enums import TipoLocalizacao  # Importado do enums.py

if TYPE_CHECKING:
    from models.lote import Lote


class Localizacao(Base):
    __tablename__ = "localizacoes"

    # Chave Primária
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Identificação Única (ex: "R01-P02-N01")
    codigo: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    descricao: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Categoria do espaço físico na fábrica
    tipo: Mapped[TipoLocalizacao] = mapped_column(
        SQLEnum(TipoLocalizacao, name="tipo_localizacao_enum"),
        default=TipoLocalizacao.ALMOXARIFADO,
        nullable=False,
    )

    # Status de disponibilidade para uso
    ativo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Capacidade máxima recomendada de lotes/pallets (Opcional)
    capacidade_maxima: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
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

    # Relacionamentos
    lotes: Mapped[List["Lote"]] = relationship(
        "Lote",
        back_populates="localizacao",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Localizacao(codigo='{self.codigo}', tipo='{self.tipo.value}', ativo={self.ativo})>"