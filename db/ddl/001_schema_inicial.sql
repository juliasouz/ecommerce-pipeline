-- DDL para PostgreSQL
-- Removendo tabelas caso já existam para facilitar a recriação (opcional)
DROP TABLE IF EXISTS entrega CASCADE;
DROP TABLE IF EXISTS forma_pagamento CASCADE;
DROP TABLE IF EXISTS pedido_produto CASCADE;
DROP TABLE IF EXISTS produtos CASCADE;
DROP TABLE IF EXISTS fornecedor CASCADE;
DROP TABLE IF EXISTS pedidos CASCADE;
DROP TABLE IF EXISTS cliente CASCADE;

CREATE TABLE cliente (
    id_cliente SERIAL PRIMARY KEY,
    endereco VARCHAR(255) NOT NULL,
    tipo_cliente VARCHAR(2) NOT NULL,
    nome_razao_social VARCHAR(255) NOT NULL,
    cpf VARCHAR(20),
    cnpj VARCHAR(20),
    CONSTRAINT chk_tipo_cliente CHECK (
        (tipo_cliente = 'PF' AND cpf IS NOT NULL AND cnpj IS NULL) OR 
        (tipo_cliente = 'PJ' AND cnpj IS NOT NULL AND cpf IS NULL)
    )
);

CREATE TABLE fornecedor (
    id_fornecedor SERIAL PRIMARY KEY,
    razao_social VARCHAR(255) NOT NULL,
    cnpj VARCHAR(20) NOT NULL
);

CREATE TABLE produtos (
    id_produto SERIAL PRIMARY KEY,
    categoria VARCHAR(255) NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    id_fornecedor INTEGER NOT NULL REFERENCES fornecedor(id_fornecedor),
    valor DECIMAL(10,2) NOT NULL,
    CONSTRAINT chk_valor_produto_positivo CHECK (valor > 0)
);

CREATE TABLE pedidos (
    id_pedido SERIAL PRIMARY KEY,
    status_do_pedido VARCHAR(50) NOT NULL,
    id_cliente INTEGER NOT NULL REFERENCES cliente(id_cliente),
    descricao VARCHAR(255) NOT NULL,
    data_pedido TIMESTAMP NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL DEFAULT 0,
    frete DECIMAL(10,2) NOT NULL DEFAULT 0,
    periodo_carencia_devolucao_dias INTEGER,
    CONSTRAINT chk_status_do_pedido_valido CHECK (status_do_pedido IN ('PENDENTE', 'PAGO', 'ENVIADO', 'ENTREGUE', 'CANCELADO')),
    CONSTRAINT chk_valor_total_positivo CHECK (valor_total >= 0),
    CONSTRAINT chk_frete_positivo CHECK (frete >= 0)
);

CREATE TABLE pedido_produto (
    id_pedido INTEGER NOT NULL REFERENCES pedidos(id_pedido),
    id_produto INTEGER NOT NULL REFERENCES produtos(id_produto),
    quantidade INTEGER NOT NULL DEFAULT 1,
    valor_unitario DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id_pedido, id_produto),
    CONSTRAINT chk_quantidade_positiva CHECK (quantidade > 0),
    CONSTRAINT chk_valor_unitario_positivo CHECK (valor_unitario >= 0)
);

CREATE TABLE forma_pagamento (
    id_forma_pagamento SERIAL PRIMARY KEY,
    id_cliente INTEGER NOT NULL REFERENCES cliente(id_cliente),
    tipo_pagamento VARCHAR(50) NOT NULL,
    detalhes VARCHAR(255) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE entrega (
    id_entrega SERIAL PRIMARY KEY,
    id_pedido INTEGER NOT NULL REFERENCES pedidos(id_pedido),
    status_entrega VARCHAR(50) NOT NULL,
    codigo_rastreio VARCHAR(255),
    data_atualizacao TIMESTAMP NOT NULL
);

-- Índices adicionais para otimização
CREATE INDEX idx_pedidos_id_cliente ON pedidos (id_cliente);
CREATE INDEX idx_pedidos_status ON pedidos (status_do_pedido);
CREATE INDEX idx_pedido_produto_id_pedido ON pedido_produto (id_pedido);
CREATE INDEX idx_pedido_produto_id_produto ON pedido_produto (id_produto);
CREATE INDEX idx_entrega_pedido ON entrega (id_pedido);
