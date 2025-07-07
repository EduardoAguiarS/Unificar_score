import streamlit as st
import pandas as pd
from pathlib import Path
import zipfile
import shutil
import re

st.set_page_config(page_title="Unificador de Scores", layout="wide")
st.title("📊 Unificação de Scores das Igrejas por Mês")

uploaded_zip = st.file_uploader("📁 Selecione o arquivo ZIP contendo as pastas de dados mensais", type="zip")


st.markdown("---")
igrejas_csv = st.file_uploader("📅 Envie o arquivo com os dados das igrejas (colunas esperadas: 'id' e 'data_cadastro')", type="csv")

df_igrejas = None
if igrejas_csv:
    try:
        df_igrejas = pd.read_csv(igrejas_csv)

        st.write("Colunas do CSV de igrejas:", list(df_igrejas.columns))

        def achar_coluna(cols, pattern):
            pattern_norm = re.sub(r"[^a-z0-9]", "", pattern.lower())
            for c in cols:
                c_norm = re.sub(r"[^a-z0-9]", "", c.lower())
                if c_norm == pattern_norm:
                    return c
            return None

        col_id = achar_coluna(df_igrejas.columns, "id")
        col_data = achar_coluna(df_igrejas.columns, "data_cadastro")

        if not col_id or not col_data:
            st.warning(f"⚠️ O arquivo de igrejas deve conter as colunas 'id' e 'data_cadastro'.\nEncontrado: {list(df_igrejas.columns)}")
            df_igrejas = None
        else:
            df_igrejas = df_igrejas.rename(columns={
                col_id: "Id Igreja",
                col_data: "Data Cadastro"
            })

            df_igrejas["Id Igreja"] = (
                df_igrejas["Id Igreja"]
                .astype(str)
                .str.replace(".", "", regex=False)
                .str.extract(r"(\d+)", expand=False)
                .fillna("0")
            )

            df_igrejas["Data Cadastro"] = pd.to_datetime(df_igrejas["Data Cadastro"], errors="coerce")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo de igrejas: {e}")

if uploaded_zip:
    temp_dir = Path("temp_folder")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()

    zip_path = temp_dir / uploaded_zip.name
    with open(zip_path, "wb") as f:
        f.write(uploaded_zip.getbuffer())

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    dados_root = next((p for p in temp_dir.iterdir() if p.is_dir() and p.name.lower() == "dados"), temp_dir)
    pastas_mensais = sorted([p for p in dados_root.iterdir() if p.is_dir()])

    if not pastas_mensais:
        st.warning("🚫 Nenhuma subpasta mensal encontrada dentro do arquivo ZIP.")
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

                        df["Id Igreja"] = (
                            df["Id Igreja"]
                            .astype(str)
                            .str.replace(".", "", regex=False)
                            .str.extract(r"(\d+)", expand=False)
                            .fillna("0")
                        )

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
                            .str.extract(r"(\d+\.?\d*)", expand=False)
                            .fillna("0")
                            .astype(float)
                            .astype(int)
                        )

                    resultado["Score Total"] = resultado[score_cols].sum(axis=1).astype(int)
                    resultado = resultado.sort_values(by="Score Total", ascending=False)

                    if df_igrejas is not None:
                        resultado = pd.merge(resultado, df_igrejas, on="Id Igreja", how="left")

                        igrejas_sem_data = resultado[resultado["Data Cadastro"].isna()]
                        if not igrejas_sem_data.empty:
                            st.warning(f"⚠️ {len(igrejas_sem_data)} igrejas não possuem data de cadastro na planilha enviada.")

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
