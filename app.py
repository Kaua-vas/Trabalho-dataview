import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from pathlib import Path
import plotly.express as px

# Configuração da página
st.set_page_config(layout="wide", page_title="Gastos Parlamentares", page_icon="💼")
st.markdown("""
    <style>
        .css-1v0mbdj.eknhn3m10 { padding: 1rem 1rem 0 1rem; }
        .deputado-header {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            gap: 1rem;
        }
        .deputado-foto {
            border: 2px solid #888;
            border-radius: 10px;
            overflow: hidden;
            width: 100px;
            height: 130px;
        }
        .deputado-info h3 {
            margin: 0 0 4px 0;
        }
        .home-button {
            margin-bottom: 20px;
        }
        .st-emotion-cache-z5fcl4 { margin-bottom: 0.5rem; }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho
st.title("Gastos Parlamentares")
st.markdown("---")

# Data de atualização
csv_path = Path("dados_consolidados.csv")
ultima_modificacao = datetime.fromtimestamp(csv_path.stat().st_mtime)
st.caption(f"Dados atualizados em {ultima_modificacao.strftime('%d/%m/%Y às %H:%M')}")

# Carregando dados
df_geral = pd.read_csv("dados_consolidados.csv")
df_geral = df_geral.dropna().drop_duplicates()
df_geral['dataDocumento'] = pd.to_datetime(df_geral['dataDocumento'])
df_geral = df_geral[df_geral['dataDocumento'].dt.year == datetime.now().year]
df_geral['mes'] = df_geral['dataDocumento'].dt.to_period("M").astype(str)

# Dicionário de deputados
dep_dict = {
    f"{row['nome']}": {'id': row['id'], 'nome': row['nome']}
    for _, row in df_geral[['id', 'nome']].drop_duplicates().iterrows()
}

dep_keys = list(dep_dict.keys())

# Estado da sessão
if 'selecionado' not in st.session_state:
    st.session_state.selecionado = ""
if 'busca' not in st.session_state:
    st.session_state.busca = ""

# Função para resetar busca e voltar à página inicial
def reset_busca():
    st.session_state.selecionado = ""
    st.session_state.busca = ""
    st.query_params.clear()
    st.rerun()

# Botão Home funcional
st.button("𐤿", on_click=reset_busca)

# Barra de seleção
dep_nome = st.selectbox("Selecione o deputado", options=[""] + sorted(dep_keys), key="busca", index=0, placeholder="Digite o nome do deputado...")
if dep_nome:
    st.session_state.selecionado = dep_nome

# Página de deputado individual
if st.session_state.selecionado:
    dep_id = dep_dict[st.session_state.selecionado]['id']
    nome = st.session_state.selecionado
    photo_url = f"https://www.camara.leg.br/internet/deputado/bandep/{dep_id}.jpg"

    df = df_geral[df_geral['id'] == dep_id].copy()
    total_gasto_dep = df['valorDocumento'].sum()

    st.markdown(f"""
        <div class='deputado-header'>
            <div class='deputado-foto'>
                <img src='{photo_url}' width='100' height='130'/>
            </div>
            <div class='deputado-info'>
                <h3>{nome}</h3>
                <p><strong>Total gasto em {datetime.now().year}:</strong> R$ {total_gasto_dep:,.2f}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.warning("Nenhuma despesa encontrada para este deputado.")
        st.stop()

    tabs = st.tabs(["Gasto Mensal", "Por Tipo", "Fornecedores", "Detalhes"])

    with tabs[0]:
        gastos_mes = df.groupby('mes')['valorDocumento'].sum().reset_index()
        fig1 = px.line(gastos_mes, x='mes', y='valorDocumento', title='Gasto Mensal',
                      labels={'valorDocumento': 'Valor (R$)', 'mes': 'Mês'}, template='plotly_white')
        fig1.update_traces(mode="lines+markers", marker=dict(size=6), hovertemplate='Mês: %{x}<br>R$ %{y:,.2f}')
        st.plotly_chart(fig1, use_container_width=True)

    with tabs[1]:
        gastos_tipo = df.groupby('tipoDespesa')['valorDocumento'].sum().sort_values(ascending=False).reset_index()
        fig2 = px.bar(gastos_tipo, x='valorDocumento', y='tipoDespesa', orientation='h',
                      title='Gasto por Tipo de Despesa', template='plotly_white')
        fig2.update_traces(hovertemplate='%{y}<br>R$ %{x:,.2f}')
        st.plotly_chart(fig2, use_container_width=True)

    with tabs[2]:
        top_forn = df.groupby('nomeFornecedor')['valorDocumento'].sum().nlargest(10).reset_index()
        fig4 = px.pie(top_forn, values='valorDocumento', names='nomeFornecedor', title='Top 10 Fornecedores')
        fig4.update_traces(textposition='outside', textinfo='label+percent', hovertemplate='%{label}<br>R$ %{value:,.2f}')
        st.plotly_chart(fig4, use_container_width=True)

    with tabs[3]:
        st.dataframe(df[['dataDocumento', 'tipoDespesa', 'valorDocumento', 'nomeFornecedor']])
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button(label="Baixar Excel", data=buffer.getvalue(), file_name="gastos.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

else:
    st.markdown("Este painel apresenta uma visão geral dos gastos parlamentares.")
    total_gasto = df_geral['valorDocumento'].sum()
    st.subheader(f"Valor total de gastos este ano: R$ {total_gasto:,.2f}")

    geral_tabs = st.tabs(["Top 10 Deputados", "Evolução Mensal Geral", "Heatmap de Tipos", "Tabela Consolidada"])

    with geral_tabs[0]:
        top10 = df_geral.groupby('nome')['valorDocumento'].sum().nlargest(10).reset_index().iloc[::-1]
        fig_bar = px.bar(top10, x='valorDocumento', y='nome', orientation='h',
                         title='Top 10 Deputados por Gastos Totais',
                         labels={'valorDocumento': 'Gasto Total (R$)', 'nome': 'Deputado'})
        fig_bar.update_traces(hovertemplate='%{y}<br>R$ %{x:,.2f}')
        st.plotly_chart(fig_bar, use_container_width=True)

    with geral_tabs[1]:
        mensal = df_geral.groupby('mes')['valorDocumento'].sum().reset_index()
        fig_line = px.line(mensal, x='mes', y='valorDocumento', title='Gasto Total por Mês (Todos Deputados)')
        fig_line.update_traces(mode="lines+markers", marker=dict(size=6), hovertemplate='Mês: %{x}<br>R$ %{y:,.2f}')
        st.plotly_chart(fig_line, use_container_width=True)

    with geral_tabs[2]:
        pivot = df_geral.pivot_table(index='tipoDespesa', columns='mes', values='valorDocumento', aggfunc='sum', fill_value=0)
        fig_heat = px.imshow(pivot, title='Distribuição de Gastos por Tipo (Heatmap)', color_continuous_scale='Blues')
        fig_heat.update_traces(hovertemplate='Tipo: %{y}<br>Mês: %{x}<br>R$ %{z:,.2f}')
        st.plotly_chart(fig_heat, use_container_width=True)

    with geral_tabs[3]:
        st.dataframe(df_geral[['dataDocumento', 'mes', 'tipoDespesa', 'valorDocumento', 'nome']])
        buffer = BytesIO()
        df_geral.to_excel(buffer, index=False)
        st.download_button(label="Baixar Excel Consolidado", data=buffer.getvalue(), file_name="gastos_consolidados.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
