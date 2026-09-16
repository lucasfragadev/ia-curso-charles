import os
import pandas as pd
from datetime import datetime
from auditoria_core import validar_linha_hgca, validar_linha_hgc, extrair_escala_plantao

# ==========================================
# CONFIGURAÇÕES E CONSTANTES
# ==========================================
PASTA_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Aula02", "documentos", "procedimentos-sus"))
PASTA_DOCS = os.path.join(PASTA_BASE, "docs")
PASTA_DADOS = os.path.join(PASTA_BASE, "data")
PASTA_SAIDA = os.path.join(PASTA_BASE, "auditoria")

ARQUIVO_SIGTAP = os.path.join(PASTA_DADOS, "exclusivo - procedimentos_cbo_225260_com_valores.xlsx")
ARQUIVO_ESCALA = os.path.join(PASTA_DOCS, "ESCALA NEUROCIRURGIA AGOSTO 2026- FATURAMENTO para o scripts.xlsx")
ARQUIVO_HGCA = os.path.join(PASTA_DOCS, "1- AGOSTO  NEUROCIRURGIA 2026 - HOSPITAL versao para o script.xlsx")
ARQUIVO_HGC = os.path.join(PASTA_DOCS, "PLANILHA AGOSTO HGC para o script.xlsx")

def carregar_sigtap() -> dict:
    df = pd.read_excel(ARQUIVO_SIGTAP, dtype={"CODIGO": str}, engine="openpyxl")
    df["CODIGO"] = df["CODIGO"].astype(str).str.strip().str.zfill(10)
    return dict(zip(df["CODIGO"], df["valorSP"]))

def salvar_relatorio(df: pd.DataFrame, prefixo: str):
    agora = datetime.now()
    pasta_dia = os.path.join(PASTA_SAIDA, agora.strftime("%Y-%m-%d"))
    os.makedirs(pasta_dia, exist_ok=True)
    
    nome_arquivo = f"{prefixo}_{agora.strftime('%H-%M-%S')}.xlsx"
    caminho_completo = os.path.join(pasta_dia, nome_arquivo)
    
    # Criar abas separadas, mantendo só as linhas que geraram status e as divergentes
    df_filtrado = df[df["STATUS_AUDITORIA"].notna() & (df["STATUS_AUDITORIA"] != "")]
    df_divergentes = df_filtrado[df_filtrado["STATUS_AUDITORIA"] != "OK"]
    
    with pd.ExcelWriter(caminho_completo, engine="openpyxl") as writer:
        df_filtrado.to_excel(writer, sheet_name="Detalhado", index=False)
        df_divergentes.to_excel(writer, sheet_name="Divergencias", index=False)
        
    print(f"-> Relatório salvo em: {caminho_completo}")

def auditar_hgca(dict_sigtap: dict, escala_dict: dict):
    print("Iniciando auditoria HGCA (Modelo 01)...")
    df = pd.read_excel(ARQUIVO_HGCA, sheet_name="AGOSTO  2026", header=9, engine="openpyxl")
    
    colunas = df.columns.tolist()
    # Preenche as células mescladas (N°, Nome, Data da cirurgia, Número de registro) para médicos adicionais
    df[colunas[0:4]] = df[colunas[0:4]].ffill()
    
    resultados = []
    for idx, row in df.iterrows():
        linha_dict = {
            "codigo_sigtap": row.get(colunas[4]),
            "descritivo": row.get(colunas[5]),
            "valor_sp": row.get(colunas[6]),
            "profissional": row.get(colunas[7]),
            "data_cirurgia": row.get(colunas[2])
        }
        
        status = validar_linha_hgca(linha_dict, dict_sigtap, escala_dict)
        
        if status:  # Se não for vazio (não é TOTAL ou linha inválida)
            nova_linha = row.to_dict()
            nova_linha["STATUS_AUDITORIA"] = " | ".join(status)
            resultados.append(nova_linha)

    if resultados:
        df_resultado = pd.DataFrame(resultados)
        salvar_relatorio(df_resultado, "auditoria_hgca")
        print(f"Auditoria HGCA concluída. {len(resultados)} procedimentos analisados.")

def auditar_hgc(dict_sigtap: dict, escala_dict: dict):
    print("Iniciando auditoria HGC (Modelo 02)...")
    df = pd.read_excel(ARQUIVO_HGC, sheet_name="HGC PROD AGOSTO 2026 ", header=4, engine="openpyxl")
    
    col_numero = df.columns[0]
    df = df[df[col_numero].astype(str).str.replace(".0", "", regex=False).str.strip().str.isdigit()]
    
    colunas = df.columns.tolist()
    
    resultados = []
    for idx, row in df.iterrows():
        linha_dict = {
            "codigo_sigtap": row.get(colunas[5]),
            "valor_proc": row.get(colunas[9]),
            "valor_princ": row.get(colunas[10]),
            "valor_aux": row.get(colunas[11]),
            "cirurgiao": row.get(colunas[7]),
            "auxiliar": row.get(colunas[8]),
            "data": row.get(colunas[3])
        }
        
        status = validar_linha_hgc(linha_dict, dict_sigtap, escala_dict)
        
        if status:
            nova_linha = row.to_dict()
            nova_linha["STATUS_AUDITORIA"] = " | ".join(status)
            resultados.append(nova_linha)

    if resultados:
        df_resultado = pd.DataFrame(resultados)
        salvar_relatorio(df_resultado, "auditoria_hgc")
        print(f"Auditoria HGC concluída. {len(resultados)} procedimentos analisados.")

if __name__ == "__main__":
    print("="*50)
    print("SISTEMA DE AUDITORIA SUS - V2 (COM VERIFICAÇÃO DE ESCALA E TESTES)")
    print("="*50)
    
    try:
        print("Carregando Tabela SIGTAP...")
        sigtap = carregar_sigtap()
        
        print("Carregando Escala Mensal...")
        escala = extrair_escala_plantao(ARQUIVO_ESCALA)
        
        auditar_hgca(sigtap, escala)
        print("-" * 50)
        auditar_hgc(sigtap, escala)
        print("Finalizado com sucesso!")
    except Exception as e:
        print(f"ERRO CRÍTICO: {e}")
