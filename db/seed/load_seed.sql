-- Script para carregar os dados CSV gerados no banco de dados
-- Uso recomendado via psql:
-- psql -U usuario -d banco -f db/seed/load_seed.sql

-- Carregando as tabelas independentes primeiro
\copy cliente(id_cliente, endereco, tipo_cliente, nome_razao_social, cpf, cnpj) FROM 'db/seed/cliente.csv' DELIMITER ',' CSV HEADER NULL '';

\copy fornecedor(id_fornecedor, razao_social, cnpj) FROM 'db/seed/fornecedor.csv' DELIMITER ',' CSV HEADER;

-- Carregando produtos (depende de fornecedor)
\copy produtos(id_produto, categoria, descricao, id_fornecedor, valor) FROM 'db/seed/produtos.csv' DELIMITER ',' CSV HEADER;

-- Carregando pedidos e formas de pagamento (dependem de cliente)
\copy pedidos(id_pedido, status_do_pedido, id_cliente, descricao, data_pedido, valor_total, frete, periodo_carencia_devolucao_dias) FROM 'db/seed/pedidos.csv' DELIMITER ',' CSV HEADER;

\copy forma_pagamento(id_forma_pagamento, id_cliente, tipo_pagamento, detalhes, ativo) FROM 'db/seed/forma_pagamento.csv' DELIMITER ',' CSV HEADER;

-- Carregando itens do pedido (depende de pedido e produto)
\copy pedido_produto(id_pedido, id_produto, quantidade, valor_unitario) FROM 'db/seed/pedido_produto.csv' DELIMITER ',' CSV HEADER;

-- Carregando entrega (depende de pedido)
\copy entrega(id_entrega, id_pedido, status_entrega, codigo_rastreio, data_atualizacao) FROM 'db/seed/entrega.csv' DELIMITER ',' CSV HEADER;

-- Atualizar sequências (SERIALs) para evitar problemas ao inserir novos registros manualmente
SELECT setval('cliente_id_cliente_seq', (SELECT MAX(id_cliente) FROM cliente));
SELECT setval('fornecedor_id_fornecedor_seq', (SELECT MAX(id_fornecedor) FROM fornecedor));
SELECT setval('produtos_id_produto_seq', (SELECT MAX(id_produto) FROM produtos));
SELECT setval('pedidos_id_pedido_seq', (SELECT MAX(id_pedido) FROM pedidos));
SELECT setval('forma_pagamento_id_forma_pagamento_seq', (SELECT MAX(id_forma_pagamento) FROM forma_pagamento));
SELECT setval('entrega_id_entrega_seq', (SELECT MAX(id_entrega) FROM entrega));

SELECT 'Carga de dados concluída com sucesso!' AS status;
