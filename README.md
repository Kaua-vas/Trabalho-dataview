# Gastos Parlamentares - Dashboard Interativo

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Dashboard interativo para visualização e análise de gastos parlamentares da Câmara dos Deputados do Brasil, desenvolvido como trabalho acadêmico da disciplina **IAA007 - Visualização de Dados e Storytelling (Turma 2025)** do Programa de Pós-Graduação em Inteligência Artificial Aplicada da **Universidade Federal do Paraná (UFPR)**.

> Projeto em constante evolução para estudo e prática de técnicas de visualização de dados.

## 📋 Sumário

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Fonte de Dados](#-fonte-de-dados)
- [Capturas de Tela](#-capturas-de-tela)
- [Autor](#-autor)
- [Licença](#-licença)

## 🎯 Sobre o Projeto

Este projeto é uma aplicação web desenvolvida com **Streamlit** que permite visualizar, analisar e exportar dados sobre os gastos parlamentares dos deputados federais brasileiros. Os dados são coletados diretamente da API oficial de Dados Abertos da Câmara dos Deputados.

### Objetivos Acadêmicos

- Aplicar técnicas de visualização de dados
- Demonstrar habilidades em storytelling com dados
- Desenvolver interface interativa para análise exploratória
- Trabalhar com dados reais de interesse público

## ✨ Funcionalidades

### Visão Geral
- **Dashboard consolidado** com métricas principais
- **Filtro por ano** para análise temporal
- **Top 15 Deputados** com maiores gastos (gráfico horizontal)
- **Evolução mensal** dos gastos totais (gráfico de área)
- **Gastos por tipo de despesa** (top 10)
- **Distribuição de gastos** (gráfico donut)
- **Exportação de dados** em Excel

### Perfil Individual do Deputado
- **Foto e informações** do deputado selecionado
- **Métricas principais**: Total gasto, média por despesa, número de transações
- **Gráfico de gastos mensais** (barras)
- **Análise por tipo de despesa** (barras horizontais)
- **Top 10 fornecedores** (gráfico donut)
- **Tabela detalhada** de todas as despesas com busca
- **Download personalizado** em Excel

### Comparação entre Deputados
- **Comparar até 5 deputados** simultaneamente
- **Três modos de comparação**:
  - Total Gasto
  - Evolução Mensal
  - Por Tipo de Despesa
- **Tabela comparativa** com estatísticas
- **Download da comparação** em Excel

### Recursos Adicionais
- Interface moderna com design clean (sem sidebar)
- Gráficos interativos com Plotly
- Validação de dados e tratamento de erros
- Sistema de cache para melhor performance
- Containers organizados para melhor visualização

## 🛠 Tecnologias Utilizadas

- **[Python 3.8+](https://www.python.org/)** - Linguagem de programação
- **[Streamlit](https://streamlit.io/)** - Framework para criação de dashboards
- **[Pandas](https://pandas.pydata.org/)** - Manipulação e análise de dados
- **[Plotly](https://plotly.com/)** - Gráficos interativos
- **[Requests](https://requests.readthedocs.io/)** - Requisições HTTP para API
- **[OpenPyXL](https://openpyxl.readthedocs.io/)** - Geração de arquivos Excel

## 📦 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git (para clonar o repositório)

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/Kaua-vas/Trabalho-dataview.git
cd Trabalho-dataview
```

### 2. Crie um ambiente virtual (recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

## 💻 Como Usar

### Passo 1: Coletar os Dados

Execute o script de coleta de dados da API da Câmara dos Deputados:

```bash
python gerar_database.py
```

Este processo pode levar alguns minutos, dependendo da sua conexão com a internet. O script irá:
- Buscar a lista de todos os deputados ativos
- Coletar as despesas de cada deputado
- Consolidar e limpar os dados
- Gerar o arquivo `dados_consolidados.csv`

**Saída esperada:**
```
======================================================================
🚀 Iniciando coleta de dados da Câmara dos Deputados
======================================================================

🔍 Buscando lista de deputados...
✅ 513 deputados encontrados.

----------------------------------------------------------------------
Coletando despesas dos deputados...
----------------------------------------------------------------------
[  1/513] João Silva                                          (PT/SP) ✅ 245 despesas
[  2/513] Maria Santos                                        (PSDB/RJ) ✅ 189 despesas
...
```

### Passo 2: Executar o Dashboard

Inicie a aplicação Streamlit:

```bash
streamlit run app.py
```

O dashboard abrirá automaticamente no seu navegador padrão em `http://localhost:8501`

### Passo 3: Explorar os Dados

1. **Página Inicial**: Visualize estatísticas gerais e rankings
2. **Selecione um deputado**: Use o seletor para ver detalhes individuais
3. **Filtre por ano**: Use o filtro na sidebar
4. **Exporte dados**: Clique nos botões de download para gerar relatórios em Excel

## 📁 Estrutura do Projeto

```
Trabalho-dataview/
│
├── app.py                      # Aplicação principal Streamlit
├── gerar_database.py           # Script de coleta de dados da API
├── dados_consolidados.csv      # Base de dados consolidada (gerada)
├── requirements.txt            # Dependências do projeto
├── README.md                   # Documentação do projeto
├── .gitignore                  # Arquivos ignorados pelo Git
└── __pycache__/               # Cache Python (ignorado)
```

## 🌐 Fonte de Dados

Os dados são coletados da [API de Dados Abertos da Câmara dos Deputados](https://dadosabertos.camara.leg.br/), que fornece acesso público a informações sobre:

- Deputados federais em exercício
- Despesas parlamentares por categoria
- Fornecedores e valores
- Datas e documentos fiscais

### Endpoints Utilizados

- `/api/v2/deputados` - Lista de deputados
- `/api/v2/deputados/{id}/despesas` - Despesas por deputado

## 📸 Capturas de Tela

*(Adicione prints do dashboard aqui)*

### Dashboard Geral
- Visão consolidada com métricas principais
- Gráficos de evolução temporal
- Rankings de gastos

### Perfil do Deputado
- Informações e foto do deputado
- Análises detalhadas de gastos
- Gráficos interativos

## 👨‍🎓 Autor

**Kaua Vasconcelos**

- GitHub: [@Kaua-vas](https://github.com/Kaua-vas)
- Instituição: Universidade Federal do Paraná (UFPR)
- Curso: Pós-Graduação em Inteligência Artificial Aplicada
- Disciplina: IAA007 - Visualização de Dados e Storytelling (Turma 2025)

## 📄 Licença

Este projeto é de código aberto e está disponível sob a [Licença MIT](LICENSE).

---

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abrir um Pull Request

## 📞 Suporte

Se você encontrar algum problema ou tiver sugestões, por favor abra uma [issue](https://github.com/Kaua-vas/Trabalho-dataview/issues) no GitHub.

---

**Desenvolvido com ❤️ para o curso de IA Aplicada da UFPR**