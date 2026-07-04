-- ==============================================================================
-- ECOMMERCE PIPELINE: Consultas Analíticas (Views e KPIs)
-- ==============================================================================

-- 1. VIEW: Receita Mensal Consolidada (Ignorando Pedidos Cancelados)
CREATE OR REPLACE VIEW vw_receita_mensal AS
SELECT 
    TO_CHAR(data_pedido, 'YYYY-MM') AS mes_ano,
    COUNT(id_pedido) AS total_pedidos,
    SUM(valor_total) AS receita_total,
    AVG(valor_total) AS ticket_medio
FROM 
    pedidos
WHERE 
    status_do_pedido != 'CANCELADO'
GROUP BY 
    TO_CHAR(data_pedido, 'YYYY-MM')
ORDER BY 
    mes_ano;

-- 2. VIEW: Top Categorias Mais Vendidas em Volume e Faturamento
CREATE OR REPLACE VIEW vw_top_categorias AS
SELECT 
    p.categoria,
    SUM(pp.quantidade) AS volume_vendido,
    SUM(pp.quantidade * pp.valor_unitario) AS receita_gerada
FROM 
    produtos p
JOIN 
    pedido_produto pp ON p.id_produto = pp.id_produto
JOIN 
    pedidos pd ON pp.id_pedido = pd.id_pedido
WHERE 
    pd.status_do_pedido != 'CANCELADO'
GROUP BY 
    p.categoria
ORDER BY 
    receita_gerada DESC;

-- 3. VIEW: Perfil de Faturamento (PF vs PJ)
CREATE OR REPLACE VIEW vw_receita_por_perfil AS
SELECT 
    c.tipo_cliente,
    COUNT(DISTINCT c.id_cliente) AS quantidade_clientes_ativos,
    COUNT(p.id_pedido) AS total_pedidos,
    SUM(p.valor_total) AS receita_total
FROM 
    cliente c
JOIN 
    pedidos p ON c.id_cliente = p.id_cliente
WHERE 
    p.status_do_pedido != 'CANCELADO'
GROUP BY 
    c.tipo_cliente;

-- 4. VIEW: Desempenho Logístico (Tempo de Entrega)
CREATE OR REPLACE VIEW vw_desempenho_logistico AS
SELECT 
    p.id_pedido,
    p.data_pedido,
    e.data_atualizacao AS data_entrega,
    e.status_entrega,
    AGE(e.data_atualizacao, p.data_pedido) AS tempo_decorrido
FROM 
    pedidos p
JOIN 
    entrega e ON p.id_pedido = e.id_pedido
WHERE 
    e.status_entrega = 'ENTREGUE';
