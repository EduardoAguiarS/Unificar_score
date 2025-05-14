# 📊 Unificador de Scores das Igrejas

Aplicação desenvolvida com [Streamlit](https://streamlit.io/) para unificar e analisar os scores das igrejas por mês, a partir de arquivos CSV organizados em pastas mensais. Ideal para análise de desempenho por categoria (eventos, células, comunicação etc.), exibindo gráficos, rankings e exportação dos dados unificados.

---

## ✅ Funcionalidades

- 📂 Leitura automática de arquivos CSV em pastas nomeadas por mês (ex: `jan_2025`, `fev_2025`, etc.).
- 🔄 Unificação dos dados por igreja e mês.
- 🧹 Normalização de colunas (`Id Igreja`, `Nome Igreja`, `Score`) e tratamento de valores.
- 📈 Geração de gráfico de barras com as 10 igrejas com maior score.
- 🔍 Filtro de igrejas por nome.
- 💾 Exportação da planilha unificada por mês.

---

## 📁 Estrutura de Pastas Esperada

A aplicação espera que os arquivos estejam organizados assim:
```
dados/
├── jan_2025/
│ ├── score_eventos.csv
│ └── score_celulas.csv
├── fev_2025/
│ ├── score_eventos.csv
│ └── score_celulas.csv
```

Cada arquivo `.csv` deve conter obrigatoriamente as colunas:

- `Id Igreja`
- `Nome Igreja`
- `Score`

---

## 🚀 Como Executar Localmente

1. **Clone o repositório:**

```bash
git clone https://github.com/seu-usuario/unificador-scores.git
cd unificador-scores
```

Instale as dependências:
```bash
pip install -r requirements.txt
```

Execute o App
```bash
streamlit run unificador_scores_app.py
```
Selecione a pasta dados/ quando solicitado pela interface do Streamlit.