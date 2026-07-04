import requests
import psycopg
import time
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

API_URL = 'http://localhost:8000'
DB_URI = os.getenv('DB_URI', 'postgresql://postgres:postgres@localhost:5432/ecommerce_db')

def get_connection():
    return psycopg.connect(DB_URI)

def ingest_from_api(conn):
    print("Buscando Pedidos da API...")
    try:
        response = requests.get(f"{API_URL}/pedidos?limit=500")
        response.raise_for_status()
        records = response.json()
    except Exception as e:
        print("Erro ao acessar API. O FastAPI (uvicorn) está rodando?", e)
        return 0
        
    if not records:
        return 0

    upsert_query = """
    INSERT INTO raw_pedidos (
        id_pedido, status_do_pedido, id_cliente, descricao, data_pedido, 
        valor_total, frete, periodo_carencia_devolucao_dias
    ) VALUES (
        %(id_pedido)s, %(status_do_pedido)s, %(id_cliente)s, %(descricao)s, %(data_pedido)s,
        %(valor_total)s, %(frete)s, %(periodo_carencia_devolucao_dias)s
    )
    ON CONFLICT (id_pedido) DO UPDATE SET
        status_do_pedido = EXCLUDED.status_do_pedido,
        valor_total = EXCLUDED.valor_total,
        _loaded_at = CURRENT_TIMESTAMP;
    """
    
    for r in records:
        r['periodo_carencia_devolucao_dias'] = r['periodo_carencia_devolucao_dias'] if r['periodo_carencia_devolucao_dias'] else None
        
    with conn.cursor() as cur:
        cur.executemany(upsert_query, records)
        
    conn.commit()
    print(f"✅ Pedidos ingeridos via API: {len(records)}")
    return len(records)

if __name__ == '__main__':
    t0 = time.time()
    try:
        conn = get_connection()
        ingest_from_api(conn)
        conn.close()
        print(f"Ingestão API completa em {time.time() - t0:.2f}s!")
    except Exception as e:
        print(e)
