import pytest
import psycopg
import sys
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, '.env'))

from ingestion import ingest_csv

DB_URI = os.getenv('DB_URI', 'postgresql://postgres:postgres@localhost:5432/ecommerce_db')

@pytest.fixture(scope="module")
def db_connection():
    try:
        conn = psycopg.connect(DB_URI)
        yield conn
    except Exception as e:
        pytest.skip(f"Banco de dados não está rodando localmente para testes: {e}")
    finally:
        if 'conn' in locals() and not conn.closed:
            conn.close()

def test_ingest_csv_idempotency(db_connection):
    # 1. Limpa a raw table de clientes temporariamente para o teste
    with db_connection.cursor() as cur:
        cur.execute("TRUNCATE TABLE raw_clientes CASCADE;")
    db_connection.commit()
    
    # 2. Primeira Execução
    count_first = ingest_csv.ingest_clientes(db_connection)
    assert count_first > 0, "A ingestão deveria processar mais de 0 registros."
    
    with db_connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM raw_clientes;")
        db_count_1 = cur.fetchone()[0]
        
    assert db_count_1 == count_first, "A quantidade de linhas no banco deveria ser igual ao processado."
    
    # 3. Segunda Execução (Idempotência / Upsert)
    count_second = ingest_csv.ingest_clientes(db_connection)
    
    with db_connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM raw_clientes;")
        db_count_2 = cur.fetchone()[0]
        
    assert db_count_1 == db_count_2, "A reexecução não pode duplicar registros. A contagem no banco mudou!"

def test_schema_columns(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'raw_pedidos';
        """)
        columns = [row[0] for row in cur.fetchall()]
        
    expected_columns = ['id_pedido', 'status_do_pedido', 'id_cliente', 'descricao', 'data_pedido', 'valor_total', 'frete', 'periodo_carencia_devolucao_dias', '_loaded_at']
    for col in expected_columns:
        assert col in columns, f"A coluna obrigatória {col} está ausente no schema de raw_pedidos."
