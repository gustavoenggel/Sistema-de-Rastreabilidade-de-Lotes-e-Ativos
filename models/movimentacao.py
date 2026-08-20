from Database.conexao import Base  # Importa a classe Base do conexao.py
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Models.enum import TipoMovimentacao

if TYPE_CHECKING:
    from Models.localizacao import Localizacao
    from Models.lote import Lote


class GenealogiaLote(Base):
    """
    Representa a relação de consumo e ascendência/descendência entre lotes (Track & Trace).
    Mapeia a inclusão de matérias-primas/insumos (lote_pai) em produtos acabados ou intermediários (lote_filho).
    """
    __tablename__ = "genealogia_lotes"
    __table_args__ = (
        CheckConstraint("quantidade_consumida > 0", name="check_qtd_consumida_positiva"),
    )

    # Chave Primária UUID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Lote Insumo / Matéria-Prima
    lote_pai_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lotes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Lote Resultante / Produto Final
    lote_filho_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lotes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Quantidade exata do lote pai incorporada ao lote filho
    quantidade_consumida: Mapped[float] = mapped_column(
        Numeric(15, 4),
        nullable=False,
    )

    # Data/Hora do vínculo na linha de produção
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # =========================================================================
    # RELACIONAMENTOS
    # =========================================================================

    lote_pai: Mapped["Lote"] = relationship(
        "Lote",
        foreign_keys=[lote_pai_id],
        back_populates="relacoes_como_pai",
    )

    lote_filho: Mapped["Lote"] = relationship(
        "Lote",
        foreign_keys=[lote_filho_id],
        back_populates="relacoes_como_filho",
    )

    def __repr__(self) -> str:
        return (
            f"<GenealogiaLote(pai_id='{self.lote_pai_id}', "
            f"filho_id='{self.lote_filho_id}', qtd={self.quantidade_consumida})>"
        )


class HistoricoMovimentacao(Base):
    """
    Registro imutável de transações (Audit Trail).
    Qualquer entrada, transferência, consumo ou expedição gera um registro nesta tabela.
    """
    __tablename__ = "historico_movimentacoes"
    __table_args__ = (
        CheckConstraint("quantidade > 0", name="check_qtd_movimentada_positiva"),
    )

    # Chave Primária UUID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Lote transacionado
    lote_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lotes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Origem e Destino (Podem ser nulos dependendo do tipo da movimentação)
    localizacao_origem_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("localizacoes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    localizacao_destino_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("localizacoes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Tipo de operação (ENTRADA, TRANSFERENCIA, CONSUMO_PRODUCAO, etc.)
    tipo_movimentacao: Mapped[TipoMovimentacao] = mapped_column(
        SQLEnum(TipoMovimentacao, name="tipo_movimentacao_enum"),
        nullable=False,
        index=True,
    )

    # Quantidade movimentada na transação
    quantidade: Mapped[float] = mapped_column(
        Numeric(15, 4),
        nullable=False,
    )

    # Identificação do operador/sistema que realizou a ação
    usuario_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # Notas operacionais (ex: número da ordem de produção, motivo do ajuste)
    observacao: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Timestamp exato da ocorrência
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,  # Indexado para agilizar relatórios por intervalo de datas
    )

    # =========================================================================
    # RELACIONAMENTOS
    # =========================================================================

    lote: Mapped["Lote"] = relationship(
        "Lote",
        back_populates="historico_movimentacoes",
    )

    localizacao_origem: Mapped[Optional["Localizacao"]] = relationship(
        "Localizacao",
        foreign_keys=[localizacao_origem_id],
    )

    localizacao_destino: Mapped[Optional["Localizacao"]] = relationship(
        "Localizacao",
        foreign_keys=[localizacao_destino_id],
    )

    def __repr__(self) -> str:
        return (
            f"<HistoricoMovimentacao(tipo='{self.tipo_movimentacao.value}', "
            f"lote_id='{self.lote_id}', qtd={self.quantidade})>"
        )