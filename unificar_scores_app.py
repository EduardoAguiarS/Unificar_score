import streamlit as st
import pandas as pd
from pathlib import Path
import os

st.set_page_config(page_title="Unificador de Scores", layout="wide")
st.title("📊 Unificação de Scores das Igrejas por Mês")

# 🔍 Entrada: caminho para as pastas mensais (fora do projeto)
caminho = st.text_input("📁 Informe o caminho local das pastas de dados (ex: C:/meus_dados)", "")

if not caminho:
    st.info("Informe um caminho válido para continuar.")
elif not os.path.isdir(caminho):
    st.error("❌ Caminho inválido ou inexistente.")
else:
    base_path = Path(caminho)
    pastas_mensais = sorted([p for p in base_path.iterdir() if p.is_dir()])

    if not pastas_mensais:
        st.warning("🚫 Nenhuma subpasta mensal encontrada nesse caminho.")
    else:
        abas = st.tabs([p.name for p in pastas_mensais])

        for aba, pasta in zip(abas, pastas_mensais):
            with aba:
                st.header(f"📆 Mês: {pasta.name}")
                arquivos = list(pasta.glob("*.csv"))

                if not arquivos:
                    st.info(f"📁 Nenhum CSV encontrado na pasta {pasta.name}.")
                    continue

                planilhas = []
                for arquivo in arquivos:
                    try:
                        df = pd.read_csv(arquivo)
                        colunas_normalizadas = {col.strip().lower(): col for col in df.columns}

                        col_id = colunas_normalizadas.get("id igreja")
                        col_nome = colunas_normalizadas.get("nome igreja")
                        col_score = colunas_normalizadas.get("score")

                        if not all([col_id, col_nome, col_score]):
                            st.warning(f"⚠️ '{arquivo.name}' não possui colunas obrigatórias.")
                            continue

                        categoria = arquivo.stem.replace("score_", "").strip().lower()

                        df = df.rename(columns={
                            col_id: "Id Igreja",
                            col_nome: "Nome Igreja",
                            col_score: f"Score_{categoria}"
                        })

                        # Remover ponto final do ID e padronizar
                        df["Id Igreja"] = df["Id Igreja"].astype(str).str.replace(r"\.$", "", regex=True)

                        df = df[["Id Igreja", "Nome Igreja", f"Score_{categoria}"]]
                        planilhas.append(df)

                    except Exception as e:
                        st.error(f"Erro ao ler {arquivo.name}: {e}")

                if planilhas:
                    resultado = planilhas[0]
                    for df in planilhas[1:]:
                        resultado = pd.merge(resultado, df, on=["Id Igreja", "Nome Igreja"], how="outer")

                    score_cols = [col for col in resultado.columns if col.startswith("Score_")]

                    for col in score_cols:
                        resultado[col] = (
                            resultado[col]
                            .astype(str)
                            .str.replace(".", "", regex=False)
                            .str.replace(",", ".", regex=False)
                            .str.replace(r"[^\d\.]", "", regex=True)
                            .replace("", "0")
                            .astype(float)
                            .round(2)
                        )

                    resultado["Score Total"] = resultado[score_cols].sum(axis=1).round(2)

                    resultado = resultado.sort_values(by="Score Total", ascending=False)

                    filtro = st.text_input("🔍 Buscar igreja por nome", key=f"filtro_{pasta.name}")
                    if filtro:
                        resultado = resultado[resultado["Nome Igreja"].str.contains(filtro, case=False)]

                    st.subheader("🏆 Top 10 Igrejas por Score Total")
                    top10 = resultado.head(10)
                    st.bar_chart(data=top10.set_index("Nome Igreja")["Score Total"])

                    st.subheader("📋 Tabela Unificada")
                    st.dataframe(resultado)

                    csv = resultado.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Baixar CSV Unificado",
                        data=csv,
                        file_name=f"planilha_unificada_{pasta.name}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("⚠️ Nenhum dado válido encontrado.")
