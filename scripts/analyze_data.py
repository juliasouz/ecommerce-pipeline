import csv
import os
import json
from collections import defaultdict
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_DIR = os.path.join(BASE_DIR, 'db', 'seed')
OUT_DIR = os.path.join(BASE_DIR, 'docs', 'analytics')

def read_csv(filename):
    with open(os.path.join(SEED_DIR, filename), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def main():
    print("Carregando dados via standard library...")
    clientes = read_csv('cliente.csv')
    produtos = read_csv('produtos.csv')
    pedidos = read_csv('pedidos.csv')
    pedido_produto = read_csv('pedido_produto.csv')
    
    # Mapas de id
    clientes_map = {c['id_cliente']: c for c in clientes}
    produtos_map = {p['id_produto']: p for p in produtos}
    
    # KPIs
    receita_mensal = defaultdict(float)
    receita_categoria = defaultdict(float)
    receita_cliente_tipo = defaultdict(float)
    status_counts = defaultdict(int)
    
    total_receita = 0.0
    total_pedidos_validos = 0
    
    for p in pedidos:
        status = p['status_do_pedido']
        status_counts[status] += 1
        
        if status == 'CANCELADO':
            continue
            
        valor = float(p['valor_total'])
        total_receita += valor
        total_pedidos_validos += 1
        
        # Receita Mensal
        dt = datetime.strptime(p['data_pedido'], "%Y-%m-%d %H:%M:%S")
        mes_ano = f"{dt.year}-{dt.month:02d}"
        receita_mensal[mes_ano] += valor
        
        # Receita Cliente Tipo
        id_cli = p['id_cliente']
        tipo_cli = clientes_map[id_cli]['tipo_cliente']
        receita_cliente_tipo[tipo_cli] += valor
        
    for pp in pedido_produto:
        # Encontrar o status do pedido
        id_prod = pp['id_produto']
        cat = produtos_map[id_prod]['categoria']
        val = float(pp['quantidade']) * float(pp['valor_unitario'])
        receita_categoria[cat] += val

    ticket_medio = total_receita / total_pedidos_validos if total_pedidos_validos > 0 else 0

    print("Gerando Dashboard HTML com Chart.js...")
    
    # Ordenar dados
    meses_ord = sorted(receita_mensal.keys())
    receita_mensal_vals = [receita_mensal[m] for m in meses_ord]
    
    cat_ord = sorted(receita_categoria.keys(), key=lambda k: receita_categoria[k], reverse=True)[:10]
    receita_cat_vals = [receita_categoria[c] for c in cat_ord]

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Analytics - Ecommerce Pipeline</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; background-color: #020617; color: #f8fafc; margin: 0; padding: 2rem; }}
            .dashboard {{ max-width: 1200px; margin: 0 auto; }}
            h1 {{ color: #38bdf8; text-align: center; margin-bottom: 2rem; }}
            .kpi-container {{ display: flex; gap: 1rem; justify-content: center; margin-bottom: 3rem; flex-wrap: wrap; }}
            .kpi-card {{ background: #0f172a; padding: 1.5rem 2rem; border-radius: 12px; border: 1px solid #0ea5e9; text-align: center; min-width: 250px; }}
            .kpi-card h3 {{ margin: 0 0 0.5rem 0; color: #cbd5e1; font-weight: 400; font-size: 1rem; }}
            .kpi-card p {{ margin: 0; font-size: 2rem; font-weight: 800; color: #38bdf8; }}
            .charts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }}
            @media (max-width: 768px) {{ .charts-grid {{ grid-template-columns: 1fr; }} }}
            .chart-wrapper {{ background: #0f172a; padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(14, 165, 233, 0.2); }}
        </style>
    </head>
    <body>
        <div class="dashboard">
            <h1>Dashboards & Análise de Dados</h1>
            
            <div class="kpi-container">
                <div class="kpi-card">
                    <h3>Receita Total Válida</h3>
                    <p>R$ {total_receita:,.2f}</p>
                </div>
                <div class="kpi-card">
                    <h3>Ticket Médio</h3>
                    <p>R$ {ticket_medio:,.2f}</p>
                </div>
                <div class="kpi-card">
                    <h3>Total de Pedidos Válidos</h3>
                    <p>{total_pedidos_validos}</p>
                </div>
            </div>

            <div class="charts-grid">
                <div class="chart-wrapper">
                    <canvas id="chartReceitaMensal"></canvas>
                </div>
                <div class="chart-wrapper">
                    <canvas id="chartTopCat"></canvas>
                </div>
                <div class="chart-wrapper">
                    <canvas id="chartStatus"></canvas>
                </div>
                <div class="chart-wrapper">
                    <canvas id="chartPerfil"></canvas>
                </div>
            </div>
        </div>

        <script>
            Chart.defaults.color = '#cbd5e1';
            Chart.defaults.font.family = 'Inter';

            // Receita Mensal
            new Chart(document.getElementById('chartReceitaMensal'), {{
                type: 'line',
                data: {{
                    labels: {json.dumps(meses_ord)},
                    datasets: [{{
                        label: 'Receita (R$)',
                        data: {json.dumps(receita_mensal_vals)},
                        borderColor: '#0ea5e9',
                        backgroundColor: 'rgba(14, 165, 233, 0.2)',
                        fill: true,
                        tension: 0.3
                    }}]
                }},
                options: {{ plugins: {{ title: {{ display: true, text: 'Evolução da Receita Mensal' }} }} }}
            }});

            // Top Categorias
            new Chart(document.getElementById('chartTopCat'), {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(cat_ord)},
                    datasets: [{{
                        label: 'Receita (R$)',
                        data: {json.dumps(receita_cat_vals)},
                        backgroundColor: '#38bdf8'
                    }}]
                }},
                options: {{ indexAxis: 'y', plugins: {{ title: {{ display: true, text: 'Top Categorias por Receita' }} }} }}
            }});

            // Status do Pedido
            new Chart(document.getElementById('chartStatus'), {{
                type: 'doughnut',
                data: {{
                    labels: {json.dumps(list(status_counts.keys()))},
                    datasets: [{{
                        data: {json.dumps(list(status_counts.values()))},
                        backgroundColor: ['#0ea5e9', '#38bdf8', '#7dd3fc', '#0284c7', '#0369a1']
                    }}]
                }},
                options: {{ plugins: {{ title: {{ display: true, text: 'Proporção de Status dos Pedidos' }} }} }}
            }});

            // Perfil do Cliente
            new Chart(document.getElementById('chartPerfil'), {{
                type: 'pie',
                data: {{
                    labels: {json.dumps(list(receita_cliente_tipo.keys()))},
                    datasets: [{{
                        data: {json.dumps(list(receita_cliente_tipo.values()))},
                        backgroundColor: ['#0ea5e9', '#7dd3fc']
                    }}]
                }},
                options: {{ plugins: {{ title: {{ display: true, text: 'Faturamento por Tipo de Cliente (PF/PJ)' }} }} }}
            }});
        </script>
    </body>
    </html>
    """
    
    with open(os.path.join(OUT_DIR, 'dashboard.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("Análise concluída com sucesso! Dashboard gerado em docs/analytics/dashboard.html")
    
    insights = {
        "total_receita": total_receita,
        "ticket_medio": ticket_medio,
        "top_categoria": cat_ord[0] if cat_ord else None,
        "pf_vs_pj": receita_cliente_tipo
    }
    with open(os.path.join(OUT_DIR, 'insights.json'), 'w', encoding='utf-8') as f:
        json.dump(insights, f)

if __name__ == '__main__':
    main()
