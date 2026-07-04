from fastapi import FastAPI
from fastapi.responses import JSONResponse
import csv
import os

app = FastAPI(title="Mock API - E-commerce Pipeline")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_DIR = os.path.join(BASE_DIR, 'db', 'seed')

def load_csv(filename, limit=1000):
    filepath = os.path.join(SEED_DIR, filename)
    if not os.path.exists(filepath):
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [row for i, row in enumerate(reader) if i < limit]

@app.get("/")
def read_root():
    return {"message": "API Mock operante. Acesse /pedidos ou /clientes."}

@app.get("/pedidos")
def get_pedidos(limit: int = 100):

    data = load_csv('pedidos.csv', limit=limit)
    return JSONResponse(content=data)

@app.get("/clientes")
def get_clientes(limit: int = 100):

    data = load_csv('cliente.csv', limit=limit)
    return JSONResponse(content=data)
