import csv
import os
import psycopg
import time
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_DIR = os.path.join(BASE_DIR, 'db', 'seed')

load_dotenv(os.path.join(BASE_DIR, '.env'))
DB_URI = os.getenv('DB_URI', 'postgresql://postgres:postgres@localhost:5432/ecommerce_db')

def get_connection():
    return psycopg.connect(DB_URI)

def ingest_pedidos(conn):
    print("Ingerindo Pedidos...")
    filepath = os.path.join(SEED_DIR, 'pedidos.csv')
    
    upsert_query = """
    INSERT INTO raw_pedidos (
        id_pedido, status_do_pedido, id_cliente, id_forma_pagamento, descricao, data_pedido, 
        valor_total, frete, periodo_carencia_devolucao_dias
    ) VALUES (
        %(id_pedido)s, %(status_do_pedido)s, %(id_cliente)s, %(id_forma_pagamento)s, %(descricao)s, %(data_pedido)s,
        %(valor_total)s, %(frete)s, %(periodo_carencia_devolucao_dias)s
    )
    ON CONFLICT (id_pedido) DO UPDATE SET
        status_do_pedido = EXCLUDED.status_do_pedido,
        valor_total = EXCLUDED.valor_total,
        id_forma_pagamento = EXCLUDED.id_forma_pagamento,
        _loaded_at = CURRENT_TIMESTAMP;
    """
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        records = list(reader)
        
        for r in records:
            r['periodo_carencia_devolucao_dias'] = r['periodo_carencia_devolucao_dias'] if r['periodo_carencia_devolucao_dias'] else None
            
        with conn.cursor() as cur:
            cur.executemany(upsert_query, records)
    
    conn.commit()
    print(f"Pedidos ingeridos: {len(records)}")
    return len(records)

def ingest_clientes(conn):
    print("Ingerindo Clientes...")
    filepath = os.path.join(SEED_DIR, 'cliente.csv')
    
    upsert_query = """
    INSERT INTO raw_clientes (
        id_cliente, endereco, tipo_cliente, nome_razao_social, cpf, cnpj
    ) VALUES (
        %(id_cliente)s, %(endereco)s, %(tipo_cliente)s, %(nome_razao_social)s, %(cpf)s, %(cnpj)s
    )
    ON CONFLICT (id_cliente) DO UPDATE SET
        endereco = EXCLUDED.endereco,
        _loaded_at = CURRENT_TIMESTAMP;
    """
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        records = list(reader)
        
        for r in records:
            r['cpf'] = r['cpf'] if r['cpf'] else None
            r['cnpj'] = r['cnpj'] if r['cnpj'] else None
            
        with conn.cursor() as cur:
            cur.executemany(upsert_query, records)
            
    conn.commit()
    print(f"Clientes ingeridos: {len(records)}")
    return len(records)

def main():
    t0 = time.time()
    try:
        conn = get_connection()
        ingest_clientes(conn)
        ingest_pedidos(conn)
        conn.close()
        t1 = time.time()
        print(f"Ingestão CSV completa com Idempotência (UPSERT) em {t1 - t0:.2f} segundos!")
    except Exception as e:
        print("Erro na conexão ou ingestão. Verifique se o DB está no ar e o DDL 002 foi rodado.")
        print(e)

if __name__ == '__main__':
    main()
