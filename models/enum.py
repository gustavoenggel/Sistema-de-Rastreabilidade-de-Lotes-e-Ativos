from enum import Enum
from Database.conexao import Base  # Importa a classe Base do conexao.py

class StatusLote(str, Enum):
    DISPONIVEL = "DISPONIVEL"
    EM_USO = "EM_USO"
    CONSUMIDO = "CONSUMIDO"
    QUARENTENA = "QUARENTENA"
    REJEITADO = "REJEITADO"
    EXPEDIDO = "EXPEDIDO"

    @classmethod
    def permitidos_para_consumo(cls) -> list["StatusLote"]:
        """Retorna os status que autorizam o uso do lote na produção."""
        return [cls.DISPONIVEL, cls.EM_USO]


class TipoMovimentacao(str, Enum):
    ENTRADA = "ENTRADA"
    TRANSFERENCIA = "TRANSFERENCIA"
    CONSUMO_PRODUCAO = "CONSUMO_PRODUCAO"
    AJUSTE_INVENTARIO = "AJUSTE_INVENTARIO"
    EXPEDICAO = "EXPEDICAO"


class UnidadeMedida(str, Enum):
    """Padroniza as unidades aceitas no cadastro de produtos (SKU)."""

    QUILOGRAMA = "KG"
    UNIDADE = "UN"
    LITRO = "L"
    METRO = "M"
    METRO_QUADRADO = "M2"
    METRO_CUBICO = "M3"


class TipoLocalizacao(str, Enum):
    """Categoriza as zonas físicas do galpão fabril."""

    RECEBIMENTO = "RECEBIMENTO"
    ALMOXARIFADO = "ALMOXARIFADO"
    LINHA_PRODUCAO = "LINHA_PRODUCAO"
    EXPEDICAO = "EXPEDICAO"