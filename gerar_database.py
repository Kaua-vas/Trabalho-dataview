import requests
import pandas as pd
import time
from datetime import datetime

def get_deputados_com_retry(max_retries=5):
    deputados = []
    pagina = 1
    while True:
        url = f"https://dadosabertos.camara.leg.br/api/v2/deputados?pagina={pagina}&itens=100"
        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                if not data['dados']:
                    return deputados
                deputados.extend(data['dados'])
                break
            except Exception as e:
                retries += 1
                wait_time = 2 ** retries
                print(f"[tentativa {retries}] Erro na página {pagina}: {e}. Tentando novamente em {wait_time}s...")
                time.sleep(wait_time)
        else:
            print(f"Falha permanente ao buscar página {pagina}, pulando...")
            break
        pagina += 1
    return deputados

def get_despesas_deputado(dep_id, nome):
    despesas = []
    pagina = 1
    while True:
        url = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}/despesas?pagina={pagina}&itens=100"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if not data['dados']:
                break
            for d in data['dados']:
                d['id'] = dep_id
                d['nome'] = nome
                despesas.append(d)
            pagina += 1
        except Exception as e:
            print(f"Erro ao buscar despesas de {nome} (ID {dep_id}): {e}")
            break
    return despesas

def main():
    print("Buscando deputados...")
    deputados = get_deputados_com_retry()
    print(f"{len(deputados)} deputados encontrados.")

    all_despesas = []
    for i, dep in enumerate(deputados, 1):
        print(f"[{i}/{len(deputados)}] {dep['nome']} ({dep['siglaPartido']}/{dep['siglaUf']})")
        despesas = get_despesas_deputado(dep['id'], dep['nome'])
        all_despesas.extend(despesas)

    if not all_despesas:
        print("Nenhuma despesa coletada.")
        return

    df = pd.DataFrame(all_despesas)
    df['dataDocumento'] = pd.to_datetime(df['dataDocumento'], errors='coerce')
    df['mes'] = df['dataDocumento'].dt.to_period('M').astype(str)

    campos_necessarios = ['id', 'nome', 'dataDocumento', 'mes', 'tipoDespesa', 'valorDocumento', 'nomeFornecedor']
    df = df[campos_necessarios].dropna().drop_duplicates()

    df.to_csv("dados_consolidados.csv", index=False, encoding='utf-8-sig')
    print("✅ Arquivo 'dados_consolidados.csv' gerado com sucesso.")

if __name__ == "__main__":
    main()
