-- 1. Extensão para geração de UUIDs
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. ENUMS (Tipos personalizados para regras de negócio)
CREATE TYPE status_lote_enum AS ENUM (
    'DISPONIVEL',
    'EM_USO',
    'CONSUMIDO',
    'QUARENTENA',
    'REJEITADO',
    'EXPEDIDO'
);

CREATE TYPE tipo_movimentacao_enum AS ENUM (
    'ENTRADA',
    'TRANSFERENCIA',
    'CONSUMO_PRODUCAO',
    'AJUSTE_INVENTARIO',
    'EXPEDICAO'
);

-- 3. TABELA: Endereçamento do Galpão / Almoxarifado
CREATE TABLE localizacoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(50) NOT NULL UNIQUE,          -- ex: 'R01-P02-N01'
    descricao VARCHAR(255),                      -- ex: 'Rua 1, Prateleira 2, Nível 1'
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. TABELA: Cadastro de Produtos (SKU)
CREATE TABLE produtos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(50) NOT NULL UNIQUE,           -- ex: 'MAT-RAW-001'
    nome VARCHAR(255) NOT NULL,                 -- ex: 'Resina Plástica PP'
    unidade_medida VARCHAR(10) NOT NULL,        -- ex: 'KG', 'UN', 'L'
    dias_validade INTEGER,                      -- Validade padrão em dias
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 5. TABELA: Lotes Físicos de Material
CREATE TABLE lotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(100) NOT NULL UNIQUE,        -- ex: 'LOT-20260815-0001'
    produto_id UUID NOT NULL REFERENCES produtos(id) ON DELETE RESTRICT,
    localizacao_id UUID REFERENCES localizacoes(id) ON DELETE SET NULL,
    quantidade_inicial NUMERIC(15, 4) NOT NULL CHECK (quantidade_inicial >= 0),
    quantidade_atual NUMERIC(15, 4) NOT NULL CHECK (quantidade_atual >= 0),
    data_fabricacao TIMESTAMPTZ NOT NULL,
    data_validade TIMESTAMPTZ,
    status status_lote_enum NOT NULL DEFAULT 'DISPONIVEL',
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Validação: Estoque atual não pode ser maior que o inicial
    CONSTRAINT check_quantidade_valida CHECK (quantidade_atual <= quantidade_inicial)
);

-- 6. TABELA: Genealogia / Rastreabilidade Pai e Filho (Track & Trace)
CREATE TABLE genealogia_lotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lote_pai_id UUID NOT NULL REFERENCES lotes(id) ON DELETE RESTRICT,   -- Lote da Matéria-Prima
    lote_filho_id UUID NOT NULL REFERENCES lotes(id) ON DELETE CASCADE,  -- Lote do Produto Final
    quantidade_consumida NUMERIC(15, 4) NOT NULL CHECK (quantidade_consumida > 0),
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Validação: Um lote não pode ser pai de si mesmo
    CONSTRAINT check_lotes_diferentes CHECK (lote_pai_id <> lote_filho_id)
);

-- 7. TABELA: Histórico / Trilha de Auditoria das Movimentações
CREATE TABLE historico_movimentacoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lote_id UUID NOT NULL REFERENCES lotes(id) ON DELETE CASCADE,
    localizacao_origem_id UUID REFERENCES localizacoes(id) ON DELETE SET NULL,
    localizacao_destino_id UUID REFERENCES localizacoes(id) ON DELETE SET NULL,
    tipo tipo_movimentacao_enum NOT NULL,
    quantidade NUMERIC(15, 4) NOT NULL,
    observacoes TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ÍNDICES PARA ALTA PERFORMANCE
-- ============================================================================

-- Acelera busca por regra FEFO (Primeiro a Vencer, Primeiro a Sair)
CREATE INDEX idx_lotes_validade_fefo ON lotes(produto_id, data_validade ASC)
WHERE status = 'DISPONIVEL';

-- Acelera busca de localização e status
CREATE INDEX idx_lotes_localizacao ON lotes(localizacao_id);
CREATE INDEX idx_lotes_status ON lotes(status);

-- Acelera a montagem da Árvore de Genealogia (Recall)
CREATE INDEX idx_genealogia_pai ON genealogia_lotes(lote_pai_id);
CREATE INDEX idx_genealogia_filho ON genealogia_lotes(lote_filho_id);

-- Acelera relatórios de movimentação por lote e por data
CREATE INDEX idx_movimentacao_lote ON historico_movimentacoes(lote_id);
CREATE INDEX idx_movimentacao_criado_em ON historico_movimentacoes(criado_em DESC);