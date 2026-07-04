import csv
import random
import os
from datetime import datetime, timedelta
from faker import Faker

# Configuração de reprodutibilidade
Faker.seed(42)
random.seed(42)
fake = Faker('pt_BR')

# Parâmetros de quantidade
NUM_CLIENTES = 5000
NUM_FORNECEDORES = 50
NUM_PRODUTOS = 500
NUM_PEDIDOS = 50000

# Diretório de saída
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db', 'seed')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def write_csv(filename, header, data):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)
    print(f"Gerado: {filepath} ({len(data)} linhas)")

def gerar_dados():
    print("Iniciando geração de dados sintéticos...")

    # 1. Clientes
    clientes = []
    # Usaremos 1 a NUM_CLIENTES como IDs
    for i in range(1, NUM_CLIENTES + 1):
        tipo_cliente = random.choice(['PF', 'PJ'])
        endereco = fake.address().replace('\n', ', ')
        if tipo_cliente == 'PF':
            nome = fake.name()
            cpf = fake.cpf()
            cnpj = None
        else:
            nome = fake.company()
            cpf = None
            cnpj = fake.cnpj()
        
        clientes.append((i, endereco, tipo_cliente, nome, cpf if cpf else '', cnpj if cnpj else ''))
    
    write_csv('cliente.csv', ['id_cliente', 'endereco', 'tipo_cliente', 'nome_razao_social', 'cpf', 'cnpj'], clientes)

    # 2. Fornecedor
    fornecedores = []
    for i in range(1, NUM_FORNECEDORES + 1):
        fornecedores.append((i, fake.company(), fake.cnpj()))
    
    write_csv('fornecedor.csv', ['id_fornecedor', 'razao_social', 'cnpj'], fornecedores)

    # 3. Produtos
    produtos = []
    categorias = ['Eletrônicos', 'Móveis', 'Roupas', 'Alimentos', 'Livros', 'Brinquedos', 'Beleza', 'Esportes']
    for i in range(1, NUM_PRODUTOS + 1):
        categoria = random.choice(categorias)
        descricao = fake.catch_phrase()
        id_fornecedor = random.randint(1, NUM_FORNECEDORES)
        valor = round(random.uniform(10.0, 5000.0), 2)
        produtos.append((i, categoria, descricao, id_fornecedor, valor))
    
    write_csv('produtos.csv', ['id_produto', 'categoria', 'descricao', 'id_fornecedor', 'valor'], produtos)

    formas_pagamento = []
    tipos_pagto = ['Cartão de Crédito', 'Boleto', 'PIX', 'Cartão de Débito']
    id_forma = 1
    # Dicionário para guardar as formas de pagamento por cliente, para uso nos pedidos
    formas_por_cliente = {}
    
    for id_cliente in range(1, NUM_CLIENTES + 1):
        formas_cliente_atual = []
        # Cada cliente tem 1 a 3 formas de pagamento
        for _ in range(random.randint(1, 3)):
            tipo = random.choice(tipos_pagto)
            detalhes = fake.credit_card_provider() if 'Cartão' in tipo else tipo
            ativo = random.choice(['true', 'false'])
            formas_pagamento.append((id_forma, id_cliente, tipo, detalhes, ativo))
            formas_cliente_atual.append(id_forma)
            id_forma += 1
        formas_por_cliente[id_cliente] = formas_cliente_atual
            
    write_csv('forma_pagamento.csv', ['id_forma_pagamento', 'id_cliente', 'tipo_pagamento', 'detalhes', 'ativo'], formas_pagamento)

    # 5. Pedidos, Itens de Pedido e Entrega
    pedidos = []
    pedido_produtos = []
    entregas = []
    
    status_opcoes = ['PENDENTE', 'PAGO', 'ENVIADO', 'ENTREGUE', 'CANCELADO']
    
    id_entrega = 1
    for i in range(1, NUM_PEDIDOS + 1):
        id_cliente = random.randint(1, NUM_CLIENTES)
        status = random.choice(status_opcoes)
        descricao = f"Pedido #{i} do cliente {id_cliente}"
        data_pedido = fake.date_time_between(start_date='-2y', end_date='now')
        frete = round(random.uniform(0.0, 150.0), 2)
        carencia = random.choice([7, 14, 30])
        
        # Escolhe uma forma de pagamento que pertence a este cliente
        id_forma_pagamento = random.choice(formas_por_cliente[id_cliente])
        
        # Itens do pedido
        num_itens = random.randint(1, 5)
        produtos_escolhidos = random.sample(produtos, num_itens)
        
        valor_total_itens = 0
        for prod in produtos_escolhidos:
            id_prod = prod[0]
            preco_unitario = prod[4]
            qtd = random.randint(1, 4)
            valor_total_itens += preco_unitario * qtd
            pedido_produtos.append((i, id_prod, qtd, preco_unitario))
            
        valor_total = round(valor_total_itens + frete, 2)
        
        pedidos.append((i, status, id_cliente, id_forma_pagamento, descricao, data_pedido.strftime('%Y-%m-%d %H:%M:%S'), valor_total, frete, carencia))
        
        # Entrega (apenas se não for pendente/cancelado)
        if status in ['ENVIADO', 'ENTREGUE']:
            status_entrega = 'Concluída' if status == 'ENTREGUE' else 'Em Trânsito'
            codigo = fake.uuid4()[:8].upper()
            data_atualizacao = data_pedido + timedelta(days=random.randint(1, 10))
            entregas.append((id_entrega, i, status_entrega, codigo, data_atualizacao.strftime('%Y-%m-%d %H:%M:%S')))
            id_entrega += 1

    write_csv('pedidos.csv', ['id_pedido', 'status_do_pedido', 'id_cliente', 'id_forma_pagamento', 'descricao', 'data_pedido', 'valor_total', 'frete', 'periodo_carencia_devolucao_dias'], pedidos)
    write_csv('pedido_produto.csv', ['id_pedido', 'id_produto', 'quantidade', 'valor_unitario'], pedido_produtos)
    write_csv('entrega.csv', ['id_entrega', 'id_pedido', 'status_entrega', 'codigo_rastreio', 'data_atualizacao'], entregas)

    print("Geração finalizada com sucesso!")

if __name__ == '__main__':
    gerar_dados()
