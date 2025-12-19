import requests
import pandas as pd
import time
from datetime import datetime
from pathlib import Path

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

def get_despesas_deputado(dep_id, nome, ano=None, max_retries=5):
    """Busca todas as despesas de um deputado com retry automático.
    
    Args:
        dep_id: ID do deputado
        nome: Nome do deputado
        ano: Ano para filtrar (None = todos os anos)
        max_retries: Número máximo de tentativas (padrão: 5)
    """
    despesas = []
    pagina = 1
    erro_motivo = None
    
    while True:
        # Adiciona filtro de ano se especificado
        url = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}/despesas?pagina={pagina}&itens=100"
        if ano:
            url += f"&ano={ano}"
        
        # DEBUG: Log da URL para primeira página
        if pagina == 1 and erro_motivo is None:
            pass  # Silencioso para não poluir
            
        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if not data.get('dados'):
                    # Retorna despesas coletadas até agora e o motivo se for a primeira página
                    if pagina == 1 and not despesas:
                        erro_motivo = "Sem dados na API"
                    return despesas, erro_motivo
                    
                for d in data['dados']:
                    d['id'] = dep_id
                    d['nome'] = nome
                despesas.extend(data['dados'])
                pagina += 1
                time.sleep(0.3)  # Rate limiting
                break
                
            except requests.exceptions.Timeout:
                retries += 1
                erro_motivo = f"Timeout (tentativa {retries}/{max_retries})"
                if retries < max_retries:
                    wait_time = 2 ** retries  # Backoff exponencial: 2s, 4s, 8s, 16s, 32s
                    print(f"\n    Aguardando {wait_time}s antes de tentar novamente...", end="")
                    time.sleep(wait_time)
                continue  # Volta para o início do loop de retries
            except requests.exceptions.HTTPError as e:
                # Erro 400 pode significar sem dados para o ano ou deputado inválido
                if e.response.status_code == 400:
                    # Verifica se tem conteúdo JSON
                    try:
                        data = e.response.json()
                        if not data.get('dados'):
                            erro_motivo = "Sem dados disponíveis (HTTP 400)"
                            return despesas, erro_motivo
                    except:
                        pass
                    
                    # Se chegou aqui, tenta novamente
                    retries += 1
                    erro_motivo = f"Erro HTTP 400 (tentativa {retries}/{max_retries})"
                    if retries < max_retries:
                        wait_time = 3 * retries
                        print(f"\n    Aguardando {wait_time}s antes de tentar novamente...", end="")
                        time.sleep(wait_time)
                    continue
                # Outros erros HTTP são definitivos
                elif e.response.status_code == 404:
                    erro_motivo = "Deputado não encontrado (404)"
                else:
                    erro_motivo = f"Erro HTTP {e.response.status_code}"
                return despesas, erro_motivo
            except Exception as e:
                erro_motivo = f"Erro: {str(e)[:50]}"
                return despesas, erro_motivo
                
        if retries >= max_retries:
            erro_motivo = f"Timeout persistente após {max_retries} tentativas"
            break
            
    return despesas, erro_motivo

def main():
    """Função principal para coletar e consolidar dados de gastos parlamentares."""
    print("="*70)
    print("Iniciando coleta de dados da Câmara dos Deputados")
    print("="*70)
    
    ano_atual = datetime.now().year
    ano_filtro = ano_atual
    print(f"\nBuscando dados do ano: {ano_atual}")
    
    # Verificar se já existe arquivo de dados anteriores
    deputados_existentes = set()
    df_anterior = None
    if Path("dados_consolidados.csv").exists():
        print("\nArquivo anterior encontrado. Carregando dados existentes...")
        try:
            df_anterior = pd.read_csv("dados_consolidados.csv")
            deputados_existentes = set(df_anterior['id'].unique())
            print(f"Dados de {len(deputados_existentes)} deputados já coletados.")
            print("Continuando coleta apenas para deputados faltantes ou com erro...\n")
        except Exception as e:
            print(f"Erro ao ler arquivo anterior: {e}")
            print("Iniciando coleta completa...\n")
    
    inicio = time.time()
    
    print("\nBuscando lista de deputados...")
    deputados = get_deputados_com_retry()
    
    if not deputados:
        print("Erro: Nenhum deputado encontrado. Verifique sua conexão com a internet.")
        return
    
    # Filtrar apenas deputados que ainda não têm dados
    deputados_pendentes = [dep for dep in deputados if dep['id'] not in deputados_existentes]
    
    if not deputados_pendentes and df_anterior is not None:
        print(f"\nTodos os {len(deputados)} deputados já têm dados coletados!")
        print("Se deseja reprocessar todos, delete o arquivo 'dados_consolidados.csv' primeiro.")
        return
    
    total_deputados = len(deputados)
    num_pendentes = len(deputados_pendentes)
    
    if df_anterior is not None:
        print(f"{total_deputados} deputados encontrados.")
        print(f"{num_pendentes} deputados pendentes de coleta.\n")
    else:
        print(f"{total_deputados} deputados encontrados.\n")
    
    print("-"*70)
    print("Coletando despesas dos deputados...")
    print("-"*70)

    all_despesas = []
    deputados_com_dados = 0
    deputados_sem_dados = 0
    erros_por_tipo = {}
    
    # Processar apenas deputados pendentes
    for i, dep in enumerate(deputados_pendentes, 1):
        nome_partido = f"{dep['nome']:45s} ({dep['siglaPartido']}/{dep['siglaUf']})"
        print(f"[{i:3d}/{num_pendentes}] {nome_partido}", end=" ")
        
        despesas, erro_motivo = get_despesas_deputado(dep['id'], dep['nome'], ano_filtro)
        
        if despesas:
            all_despesas.extend(despesas)
            deputados_com_dados += 1
            print(f"OK - {len(despesas)} despesas")
        else:
            deputados_sem_dados += 1
            motivo = erro_motivo or "Sem dados"
            erros_por_tipo[motivo] = erros_por_tipo.get(motivo, 0) + 1
            print(f"Sem dados - {motivo}")

    if not all_despesas:
        print("\nErro: Nenhuma despesa coletada.")
        if erros_por_tipo:
            print("\nMotivos:")
            for motivo, count in sorted(erros_por_tipo.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {motivo}: {count} deputado(s)")
        return

    print("\n" + "-"*70)
    print("Processando e consolidando dados...")
    
    # Se há dados anteriores, combina com os novos
    if df_anterior is not None and not df_anterior.empty:
        df_novos = pd.DataFrame(all_despesas) if all_despesas else pd.DataFrame()
        if not df_novos.empty:
            # Processar novos dados
            df_novos['dataDocumento'] = pd.to_datetime(df_novos['dataDocumento'], errors='coerce')
            df_novos['mes'] = df_novos['dataDocumento'].dt.to_period('M').astype(str)
            # Combinar com dados anteriores
            df = pd.concat([df_anterior, df_novos], ignore_index=True)
        else:
            df = df_anterior
    else:
        df = pd.DataFrame(all_despesas)
        df['dataDocumento'] = pd.to_datetime(df['dataDocumento'], errors='coerce')
        df['mes'] = df['dataDocumento'].dt.to_period('M').astype(str)

    campos_necessarios = ['id', 'nome', 'dataDocumento', 'mes', 'tipoDespesa', 'valorDocumento', 'nomeFornecedor']
    df_original_len = len(df)
    df = df[campos_necessarios].dropna().drop_duplicates()
    
    # Salvando arquivo
    df.to_csv("dados_consolidados.csv", index=False, encoding='utf-8-sig')
    
    tempo_total = time.time() - inicio
    
    # Estatísticas finais
    total_deputados_com_dados = len(df['id'].unique())
    total_deputados_no_arquivo = total_deputados
    
    print("-"*70)
    print("ESTATÍSTICAS DA COLETA")
    print("="*70)
    print(f"Total de deputados:              {total_deputados_no_arquivo}")
    print(f"Deputados com dados no arquivo:  {total_deputados_com_dados} ({total_deputados_com_dados/total_deputados_no_arquivo*100:.1f}%)")
    print(f"Deputados sem dados:             {total_deputados_no_arquivo - total_deputados_com_dados} ({(total_deputados_no_arquivo - total_deputados_com_dados)/total_deputados_no_arquivo*100:.1f}%)")
    
    if num_pendentes > 0:
        print(f"\nNesta execução:")
        print(f"  Deputados processados:         {num_pendentes}")
        print(f"  Novos com dados:               {deputados_com_dados}")
        print(f"  Falharam:                      {deputados_sem_dados}")
    
    if erros_por_tipo:
        print(f"\nMotivos para deputados sem dados:")
        for motivo, count in sorted(erros_por_tipo.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {motivo:30s}: {count:3d} deputado(s)")
    
    print(f"\nDespesas coletadas:              {df_original_len:,}")
    print(f"Despesas válidas (após limpeza):  {len(df):,}")
    print(f"Total gasto:                     R$ {df['valorDocumento'].sum():,.2f}")
    print(f"Período dos dados:               {df['dataDocumento'].min().strftime('%d/%m/%Y')} a {df['dataDocumento'].max().strftime('%d/%m/%Y')}")
    print(f"Tempo total:                     {tempo_total:.1f}s")
    print("="*70)
    print("Arquivo 'dados_consolidados.csv' atualizado com sucesso!")
    
    if deputados_sem_dados > 0:
        print(f"\nAinda há {deputados_sem_dados} deputado(s) sem dados.")
        print("Execute novamente para tentar buscar os dados faltantes.")
    
    print("\nExecute agora: streamlit run app.py")
    print("="*70)



if __name__ == "__main__":
    main()
