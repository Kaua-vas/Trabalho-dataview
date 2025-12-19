import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(layout="wide", page_title="Gastos Parlamentares", page_icon="📊")

# Inicializar session state para manter tab ativa
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# CSS customizado
st.markdown("""
    <style>
        .block-container { padding-top: 1.5rem; }
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .main-header h1 { margin: 0; font-size: 2.5rem; font-weight: 700; }
        .main-header p { margin: 0.5rem 0 0 0; opacity: 0.95; }
        [data-testid="stSidebar"] { display: none; }
        div[data-testid="stMetricValue"] { font-size: 2rem; }
    </style>
""", unsafe_allow_html=True)

# Carregar dados
@st.cache_data
def load_data():
    csv_path = Path("dados_consolidados.csv")
    if not csv_path.exists():
        return None, None
    
    df = pd.read_csv("dados_consolidados.csv")
    df = df.dropna().drop_duplicates()
    df['dataDocumento'] = pd.to_datetime(df['dataDocumento'])
    df['mes'] = df['dataDocumento'].dt.to_period("M").astype(str)
    df['ano'] = df['dataDocumento'].dt.year
    
    ultima_mod = datetime.fromtimestamp(csv_path.stat().st_mtime)
    return df, ultima_mod

df_geral, ultima_modificacao = load_data()

if df_geral is None:
    st.error("Arquivo 'dados_consolidados.csv' não encontrado.")
    st.info("Execute: python gerar_database.py")
    st.stop()

# Header
st.markdown(f"""
    <div class="main-header">
        <h1>Painel de Gastos Parlamentares</h1>
        <p>Análise interativa das despesas da Câmara dos Deputados • Atualizado em {ultima_modificacao.strftime('%d/%m/%Y às %H:%M')}</p>
    </div>
""", unsafe_allow_html=True)

# Filtros globais
col1, col2, col3 = st.columns([2, 6, 2])
with col1:
    ano_selecionado = st.selectbox("Ano", sorted(df_geral['ano'].unique(), reverse=True))
with col3:
    st.write("")  # Espaçamento

df_filtrado = df_geral[df_geral['ano'] == ano_selecionado].copy()

# Navegação por tabs principal
tab1, tab2, tab3 = st.tabs(["Visão Geral", "Perfil do Deputado", "Comparação"])

# ============= TAB 1: VISÃO GERAL =============
with tab1:
    st.markdown("### Estatísticas Gerais")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    total_gasto = df_filtrado['valorDocumento'].sum()
    num_deputados = df_filtrado['id'].nunique()
    total_despesas = len(df_filtrado)
    media_por_dep = total_gasto / num_deputados if num_deputados > 0 else 0
    
    col1.metric("Total Gasto", f"R$ {total_gasto/1e6:.1f}M")
    col2.metric("Deputados", f"{num_deputados}")
    col3.metric("Total de Despesas", f"{total_despesas:,}")
    col4.metric("Média por Deputado", f"R$ {media_por_dep/1e3:.0f}k")
    
    st.markdown("---")
    
    # Gráficos lado a lado
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown("#### Top 15 Deputados com Maiores Gastos")
            top15 = df_filtrado.groupby('nome')['valorDocumento'].sum().nlargest(15).reset_index()
            # Ordenar do maior para o menor (crescente para exibição horizontal invertida)
            top15 = top15.sort_values('valorDocumento', ascending=True)
            fig1 = px.bar(top15, y='nome', x='valorDocumento', orientation='h',
                         color='valorDocumento', color_continuous_scale='Purples')
            fig1.update_layout(showlegend=False, height=500, xaxis_title="Valor (R$)", yaxis_title="")
            fig1.update_traces(hovertemplate='<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>')
            st.plotly_chart(fig1, width='stretch')
    
    with col2:
        with st.container():
            st.markdown("#### Evolução Mensal dos Gastos")
            mensal = df_filtrado.groupby('mes')['valorDocumento'].sum().reset_index()
            fig2 = px.area(mensal, x='mes', y='valorDocumento', 
                          color_discrete_sequence=['#667eea'])
            fig2.update_layout(height=500, xaxis_title="Mês", yaxis_title="Valor (R$)")
            fig2.update_traces(hovertemplate='<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>')
            st.plotly_chart(fig2, width='stretch')
    
    st.markdown("---")
    
    # Tipos de despesa
    col1, col2 = st.columns([6, 4])
    
    with col1:
        with st.container():
            st.markdown("#### Gastos por Tipo de Despesa")
            tipos = df_filtrado.groupby('tipoDespesa')['valorDocumento'].sum().sort_values(ascending=False).head(10).reset_index()
            # Ordenar crescente para exibir maior no topo (horizontal)
            tipos = tipos.sort_values('valorDocumento', ascending=True)
            fig3 = px.bar(tipos, x='valorDocumento', y='tipoDespesa', orientation='h',
                         color='valorDocumento', color_continuous_scale='Viridis')
            fig3.update_layout(showlegend=False, height=400, xaxis_title="Valor (R$)", yaxis_title="")
            fig3.update_traces(hovertemplate='<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>')
            st.plotly_chart(fig3, width='stretch')
    
    with col2:
        with st.container():
            st.markdown("#### Distribuição de Gastos")
            # Top 5 tipos + outros
            top5_tipos = df_filtrado.groupby('tipoDespesa')['valorDocumento'].sum().nlargest(5)
            outros = df_filtrado.groupby('tipoDespesa')['valorDocumento'].sum().sum() - top5_tipos.sum()
            
            pie_data = pd.DataFrame({
                'tipo': list(top5_tipos.index) + ['Outros'],
                'valor': list(top5_tipos.values) + [outros]
            })
            
            fig4 = px.pie(pie_data, values='valor', names='tipo', hole=0.4,
                         color_discrete_sequence=px.colors.sequential.Purples_r)
            fig4.update_layout(height=400)
            # Melhorar legibilidade: percentual fora, apenas label dentro
            fig4.update_traces(textposition='auto', textinfo='percent',
                              hovertemplate='<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>')
            st.plotly_chart(fig4, width='stretch')

# ============= TAB 2: PERFIL INDIVIDUAL =============
with tab2:
    st.markdown("### Análise Individual de Deputado")
    
    deputados_lista = sorted(df_filtrado['nome'].unique())
    deputado_selecionado = st.selectbox("Selecione um deputado:", [None] + deputados_lista, format_func=lambda x: "Selecione um deputado..." if x is None else x, key="deputado_individual")
    
    if deputado_selecionado:
        df_dep = df_filtrado[df_filtrado['nome'] == deputado_selecionado].copy()
        dep_id = df_dep['id'].iloc[0]
        total_dep = df_dep['valorDocumento'].sum()
        num_despesas_dep = len(df_dep)
        
        # Card de informações do deputado
        col1, col2, col3, col4 = st.columns([1, 3, 3, 3])
        
        with col1:
            photo_url = f"https://www.camara.leg.br/internet/deputado/bandep/{dep_id}.jpg"
            st.markdown(f'<img src="{photo_url}" width="100%" style="border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"#### {deputado_selecionado}")
            st.metric("Total Gasto", f"R$ {total_dep:,.2f}")
        
        with col3:
            st.write("")
            st.write("")
            st.metric("Total de Despesas", f"{num_despesas_dep}")
        
        with col4:
            st.write("")
            st.write("")
            ranking = df_filtrado.groupby('nome')['valorDocumento'].sum().rank(ascending=False)[deputado_selecionado]
            st.metric("Ranking", f"{int(ranking)}º de {len(deputados_lista)-1}")
        
        st.markdown("---")
        
        # Análises
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Gastos Mensais")
            mensal_dep = df_dep.groupby('mes')['valorDocumento'].sum().reset_index()
            fig = px.line(mensal_dep, x='mes', y='valorDocumento', markers=True,
                         color_discrete_sequence=['#667eea'])
            fig.update_layout(xaxis_title="Mês", yaxis_title="Valor (R$)", height=350)
            fig.update_traces(hovertemplate='<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>')
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            st.markdown("#### Por Tipo de Despesa")
            tipos_dep = df_dep.groupby('tipoDespesa')['valorDocumento'].sum().sort_values(ascending=False).head(8).reset_index()
            # Ordenar crescente para maior no topo
            tipos_dep = tipos_dep.sort_values('valorDocumento', ascending=True)
            fig = px.bar(tipos_dep, y='tipoDespesa', x='valorDocumento', orientation='h',
                        color='valorDocumento', color_continuous_scale='Purples')
            fig.update_layout(showlegend=False, xaxis_title="Valor (R$)", yaxis_title="", height=350)
            fig.update_traces(hovertemplate='<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>')
            st.plotly_chart(fig, width='stretch')
        
        st.markdown("#### Top 10 Fornecedores")
        fornecedores = df_dep.groupby('nomeFornecedor')['valorDocumento'].sum().nlargest(10).reset_index()
        # Ordenar crescente para maior no topo
        fornecedores = fornecedores.sort_values('valorDocumento', ascending=True)
        fig = px.bar(fornecedores, x='valorDocumento', y='nomeFornecedor', orientation='h',
                    color='valorDocumento', color_continuous_scale='Teal')
        fig.update_layout(showlegend=False, xaxis_title="Valor (R$)", yaxis_title="", height=400)
        fig.update_traces(hovertemplate='<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>')
        st.plotly_chart(fig, width='stretch')
        
        # Tabela de detalhes
        with st.expander("Ver todas as despesas"):
            st.dataframe(
                df_dep[['dataDocumento', 'tipoDespesa', 'valorDocumento', 'nomeFornecedor']]
                .sort_values('dataDocumento', ascending=False)
                .style.format({'valorDocumento': 'R$ {:,.2f}'}),
                width='stretch'
            )

# ============= TAB 3: COMPARAÇÃO =============
with tab3:
    st.markdown("### Comparação Entre Deputados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        deputados_comparar = st.multiselect(
            "Selecione até 5 deputados para comparar:",
            sorted(df_filtrado['nome'].unique()),
            max_selections=5,
            key="comparacao_deputados",
            default=[]
        )
    
    with col2:
        tipo_comparacao = st.radio(
            "Tipo de comparação:",
            ["Total Gasto", "Evolução Mensal", "Por Tipo de Despesa"],
            horizontal=True
        )
    
    if deputados_comparar:
        if tipo_comparacao == "Total Gasto":
            with st.container():
                df_comp = df_filtrado[df_filtrado['nome'].isin(deputados_comparar)].groupby('nome')['valorDocumento'].sum().reset_index()
                df_comp.columns = ['Deputado', 'Total Gasto']
                # Ordenar do maior para o menor
                df_comp = df_comp.sort_values('Total Gasto', ascending=False)
                
                # Usar cores discretas em vez de escala contínua
                fig = px.bar(df_comp, x='Deputado', y='Total Gasto',
                            color='Deputado', color_discrete_sequence=px.colors.qualitative.Set2)
                fig.update_layout(
                    xaxis_title="Deputado", 
                    yaxis_title="Total Gasto (R$)",
                    showlegend=False,
                    height=500
                )
                fig.update_traces(hovertemplate='<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>')
                st.plotly_chart(fig, width='stretch')
            
        elif tipo_comparacao == "Evolução Mensal":
            with st.container():
                df_comp = df_filtrado[df_filtrado['nome'].isin(deputados_comparar)].groupby(['mes', 'nome'])['valorDocumento'].sum().reset_index()
                df_comp.columns = ['Mes', 'Deputado', 'Gasto']
                
                fig = px.line(df_comp, x='Mes', y='Gasto', color='Deputado', markers=True)
                fig.update_layout(
                    xaxis_title="Mes",
                    yaxis_title="Valor (R$)",
                    height=500,
                    legend_title="Deputado"
                )
                fig.update_traces(hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>R$ %{y:,.2f}<extra></extra>')
                st.plotly_chart(fig, width='stretch')
            
        elif tipo_comparacao == "Por Tipo de Despesa":
            with st.container():
                df_comp = df_filtrado[df_filtrado['nome'].isin(deputados_comparar)].groupby(['tipoDespesa', 'nome'])['valorDocumento'].sum().reset_index()
                df_comp.columns = ['Tipo de Despesa', 'Deputado', 'Gasto']
                # Pegar top 10 tipos gerais
                top_tipos = df_filtrado.groupby('tipoDespesa')['valorDocumento'].sum().nlargest(10).index
                df_comp = df_comp[df_comp['Tipo de Despesa'].isin(top_tipos)]
                
                fig = px.bar(df_comp, x='Tipo de Despesa', y='Gasto', color='Deputado', barmode='group')
                fig.update_layout(
                    xaxis_title="Tipo de Despesa",
                    yaxis_title="Valor (R$)",
                    height=500,
                    legend_title="Deputado",
                    xaxis_tickangle=-45
                )
                fig.update_traces(hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>R$ %{y:,.2f}<extra></extra>')
                st.plotly_chart(fig, width='stretch')
        
        # Tabela comparativa
        st.markdown("#### Tabela Comparativa")
        df_tabela = df_filtrado[df_filtrado['nome'].isin(deputados_comparar)].groupby('nome').agg({
            'valorDocumento': ['sum', 'mean', 'count']
        }).round(2)
        df_tabela.columns = ['Total Gasto (R$)', 'Média por Despesa (R$)', 'Número de Despesas']
        df_tabela = df_tabela.sort_values('Total Gasto (R$)', ascending=False)
        st.dataframe(df_tabela.style.format({
            'Total Gasto (R$)': 'R$ {:,.2f}',
            'Média por Despesa (R$)': 'R$ {:,.2f}',
            'Número de Despesas': '{:,.0f}'
        }), width='stretch')
    else:
        st.info("Selecione deputados acima para começar a comparação")

# Footer
st.markdown("---")
st.caption("Desenvolvido para IAA007 - Visualização de Dados e Storytelling | UFPR 2025")
