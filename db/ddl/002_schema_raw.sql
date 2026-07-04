-- Schema da Camada Raw (Data Warehouse)
-- Tabelas projetadas para receber dados sujos de origens diversas (CSV, API)

CREATE TABLE IF NOT EXISTS raw_clientes (
    id_cliente INT UNIQUE NOT NULL, -- Chave natural (Idempotência / Upsert)
    endereco VARCHAR(255),
    tipo_cliente VARCHAR(50),
    nome_razao_social VARCHAR(255),
    cpf VARCHAR(50),
    cnpj VARCHAR(50),
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_produtos (
    id_produto INT UNIQUE NOT NULL, -- Chave natural
    categoria VARCHAR(100),
    descricao VARCHAR(255),
    id_fornecedor INT,
    valor NUMERIC(10, 2),
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_pedidos (
    id_pedido INT UNIQUE NOT NULL, -- Chave natural
    status_do_pedido VARCHAR(50),
    id_cliente INT,
    id_forma_pagamento INT,
    descricao VARCHAR(255),
    data_pedido TIMESTAMP,
    valor_total NUMERIC(10, 2),
    frete NUMERIC(10, 2),
    periodo_carencia_devolucao_dias INT,
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
