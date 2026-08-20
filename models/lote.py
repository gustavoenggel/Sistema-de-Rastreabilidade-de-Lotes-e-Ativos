from Database.conexao import Base  # Importa a classe Base do conexao.py

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Models.enum import StatusLote  # Importado do enums.py

if TYPE_CHECKING:
    from Models.localizacao import Localizacao
    from Models.movimentacao import GenealogiaLote, HistoricoMovimentacao
    from Models.produto import Produto


class Lote(Base):
    __tablename__ = "lotes"
    __table_args__ = (
        CheckConstraint("quantidade_inicial >= 0", name="check_qtd_inicial_positiva"),
        CheckConstraint("quantidade_atual >= 0", name="check_qtd_atual_positiva"),
        CheckConstraint(
            "quantidade_atual <= quantidade_inicial", name="check_quantidade_valida"
        ),
    )

    # Chave Primária UUID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Identificador Único visível/escaneável do Lote (ex: "LOT-20260818-0001")
    codigo: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    # Chaves Estrangeiras (Chão de fábrica: Produto é obrigatório, Localização pode ser nula se estiver em trânsito)
    produto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("produtos.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    localizacao_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("localizacoes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Quantidades (Precisão de 4 casas decimais para insumos fracionados)
    quantidade_inicial: Mapped[float] = mapped_column(
        Numeric(15, 4),
        nullable=False,
    )

    quantidade_atual: Mapped[float] = mapped_column(
        Numeric(15, 4),
        nullable=False,
    )

    # Datas de Controle (Fundamentais para regra FEFO)
    data_fabricacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    data_validade: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,  # Indexado para acelerar a busca FEFO
    )

    # Status Atual do Lote
    status: Mapped[StatusLote] = mapped_column(
        SQLEnum(StatusLote, name="status_lote_enum"),
        default=StatusLote.DISPONIVEL,
        nullable=False,
        index=True,
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

    # =========================================================================
    # RELACIONAMENTOS
    # =========================================================================

    produto: Mapped["Produto"] = relationship(
        "Produto",
        back_populates="lotes",
    )

    localizacao: Mapped[Optional["Localizacao"]] = relationship(
        "Localizacao",
        back_populates="lotes",
    )

    # Rastreabilidade: Lote atuando como matéria-prima (pai de outros lotes)
    relacoes_como_pai: Mapped[List["GenealogiaLote"]] = relationship(
        "GenealogiaLote",
        foreign_keys="[GenealogiaLote.lote_pai_id]",
        back_populates="lote_pai",
        lazy="select",
    )

    # Rastreabilidade: Lote atuando como produto final (filho de outros lotes)
    relacoes_como_filho: Mapped[List["GenealogiaLote"]] = relationship(
        "GenealogiaLote",
        foreign_keys="[GenealogiaLote.lote_filho_id]",
        back_populates="lote_filho",
        lazy="select",
    )

    # Trilha de Auditoria
    historico_movimentacoes: Mapped[List["HistoricoMovimentacao"]] = relationship(
        "HistoricoMovimentacao",
        back_populates="lote",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Lote(codigo='{self.codigo}', saldo={self.quantidade_atual}, status='{self.status.value}')>"