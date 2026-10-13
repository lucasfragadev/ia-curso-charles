import os
import pandas as pd
from datetime import datetime
from core.auditoria_core import validar_linha_hgca, validar_linha_hgc, extrair_escala_plantao

def carregar_sigtap(arquivo_sigtap) -> dict:
    df = pd.read_excel(arquivo_sigtap, dtype={"CODIGO": str}, engine="openpyxl")
    df["CODIGO"] = df["CODIGO"].astype(str).str.strip().str.zfill(10)
    return dict(zip(df["CODIGO"], df["valorSP"]))

def salvar_relatorio(df: pd.DataFrame, caminho_completo: str):
    nome_arquivo = f"auditoria_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    if not caminho_completo:
        pasta_dia = os.path.join("auditoria", datetime.now().strftime("%Y-%m-%d"))
        os.makedirs(pasta_dia, exist_ok=True)
        caminho_completo = os.path.join(pasta_dia, nome_arquivo)
    elif os.path.isdir(caminho_completo):
        caminho_completo = os.path.join(caminho_completo, nome_arquivo)
        
    # Remove coluna OBS e colunas Unnamed para não poluir o relatório final
    colunas_para_remover = [col for col in df.columns if col == 'OBS' or col == 'OBS ' or str(col).startswith('Unnamed')]
    if colunas_para_remover:
        df = df.drop(columns=colunas_para_remover)
        
    df_filtrado = df[df["STATUS_AUDITORIA"].notna() & (df["STATUS_AUDITORIA"] != "")]
    df_divergentes = df_filtrado[df_filtrado["STATUS_AUDITORIA"] != "OK"]
    
    with pd.ExcelWriter(caminho_completo, engine="openpyxl") as writer:
        df_filtrado.to_excel(writer, sheet_name="Detalhado", index=False)
        df_divergentes.to_excel(writer, sheet_name="Divergencias", index=False)
        
    return caminho_completo

def auditar_hgca(arquivo_planilha, arquivo_escala, arquivo_saida, arquivo_sigtap, mapeamento, linha_cabecalho=9):
    dict_sigtap = carregar_sigtap(arquivo_sigtap)
    escala_dict = extrair_escala_plantao(arquivo_escala)
    
    try:
        df = pd.read_excel(arquivo_planilha, sheet_name="AGOSTO  2026", header=linha_cabecalho, engine="openpyxl")
    except ValueError:
        df = pd.read_excel(arquivo_planilha, sheet_name=0, header=linha_cabecalho, engine="openpyxl")
    
    colunas = df.columns.tolist()
    # Pega as colunas mapeadas
    col_codigo = mapeamento.get("codigo_sigtap")
    col_desc = mapeamento.get("descritivo")
    col_valor = mapeamento.get("valor_sp")
    col_prof = mapeamento.get("profissional")
    col_data = mapeamento.get("data_cirurgia")
    col_numero = mapeamento.get("numero")
    
    # Preenche as primeiras 4 colunas (baseado no ffill antigo) - agora usamos as colunas corretas se possivel, mas como o ffill era posicional, aplicaremos ffill em todo o dataframe para evitar nulos em celulas mescladas
    df = df.ffill()
    
    resultados = []
    for idx, row in df.iterrows():
        linha_dict = {
            "codigo_sigtap": row.get(col_codigo),
            "descritivo": row.get(col_desc) if col_desc else "",
            "valor_sp": row.get(col_valor),
            "profissional": row.get(col_prof),
            "data_cirurgia": row.get(col_data)
        }
        status = validar_linha_hgca(linha_dict, dict_sigtap, escala_dict)
        if status:
            nova_linha = row.to_dict()
            nova_linha["STATUS_AUDITORIA"] = " | ".join(status)
            resultados.append(nova_linha)

    if resultados:
        df_resultado = pd.DataFrame(resultados)
        divergentes = len(df_resultado[df_resultado["STATUS_AUDITORIA"] != "OK"])
        nao_previstos = len(df_resultado[df_resultado["STATUS_AUDITORIA"].str.contains("CÓDIGO FORA DO CBO", na=False)])
        corretos = len(df) - divergentes
        caminho = salvar_relatorio(df_resultado, arquivo_saida)
        return {
            "sucesso": True, 
            "total": len(df), 
            "divergentes": divergentes,
            "corretos": corretos,
            "nao_previstos": nao_previstos,
            "perc_principal_ok": "N/A",
            "perc_auxiliar_ok": "N/A",
            "arquivo_saida": caminho
        }
        
    return {
        "sucesso": True, 
        "total": len(df), 
        "divergentes": 0, 
        "corretos": len(df),
        "nao_previstos": 0,
        "perc_principal_ok": "N/A",
        "perc_auxiliar_ok": "N/A",
        "arquivo_saida": ""
    }

def auditar_hgc(arquivo_planilha, arquivo_escala, arquivo_saida, arquivo_sigtap, mapeamento, linha_cabecalho=4):
    dict_sigtap = carregar_sigtap(arquivo_sigtap)
    escala_dict = extrair_escala_plantao(arquivo_escala)
    
    try:
        df = pd.read_excel(arquivo_planilha, sheet_name="HGC PROD AGOSTO 2026 ", header=linha_cabecalho, engine="openpyxl")
    except ValueError:
        df = pd.read_excel(arquivo_planilha, sheet_name=0, header=linha_cabecalho, engine="openpyxl")
    
    col_numero = mapeamento.get("numero") or df.columns[0]
    df = df[df[col_numero].astype(str).str.replace(".0", "", regex=False).str.strip().str.isdigit()]
    
    col_codigo = mapeamento.get("codigo_sigtap")
    col_vproc = mapeamento.get("valor_proc")
    col_vprinc = mapeamento.get("valor_principal")
    col_vaux = mapeamento.get("valor_auxiliar")
    col_cir = mapeamento.get("cirurgiao")
    col_aux = mapeamento.get("auxiliar")
    col_data = mapeamento.get("data")
    
    resultados = []
    for idx, row in df.iterrows():
        linha_dict = {
            "codigo_sigtap": row.get(col_codigo),
            "valor_proc": row.get(col_vproc),
            "valor_princ": row.get(col_vprinc),
            "valor_aux": row.get(col_vaux),
            "cirurgiao": row.get(col_cir),
            "auxiliar": row.get(col_aux),
            "data": row.get(col_data)
        }
        status = validar_linha_hgc(linha_dict, dict_sigtap, escala_dict)
        if status:
            nova_linha = row.to_dict()
            nova_linha["STATUS_AUDITORIA"] = " | ".join(status)
            resultados.append(nova_linha)

    if resultados:
        df_resultado = pd.DataFrame(resultados)
        divergentes = len(df_resultado[df_resultado["STATUS_AUDITORIA"] != "OK"])
        nao_previstos = len(df_resultado[df_resultado["STATUS_AUDITORIA"].str.contains("CÓDIGO FORA DO CBO", na=False)])
        corretos = len(df) - divergentes
        
        caminho = salvar_relatorio(df_resultado, arquivo_saida)
        return {
            "sucesso": True, 
            "total": len(df), 
            "divergentes": divergentes,
            "corretos": corretos,
            "nao_previstos": nao_previstos,
            "perc_principal_ok": "N/A",
            "perc_auxiliar_ok": "N/A",
            "arquivo_saida": caminho
        }
        
    return {
        "sucesso": True, 
        "total": len(df), 
        "divergentes": 0, 
        "corretos": len(df),
        "nao_previstos": 0,
        "perc_principal_ok": "N/A",
        "perc_auxiliar_ok": "N/A",
        "arquivo_saida": ""
    }
