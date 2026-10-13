import pandas as pd
import unicodedata
from datetime import datetime

TOLERANCIA_CENTAVOS = 0.05

def normalizar_nome(nome) -> str:
    """Remove acentos, espaços extras e deixa em maiúsculo."""
    if pd.isna(nome) or not str(nome).strip():
        return ""
    n = str(nome).strip().upper()
    n = unicodedata.normalize('NFKD', n).encode('ASCII', 'ignore').decode('utf-8')
    return n

def formatar_moeda(valor) -> float:
    try:
        return float(str(valor).replace(",", "."))
    except (ValueError, TypeError):
        return 0.0

def normalizar_codigo(cod) -> str:
    """Retorna código de 10 dígitos limpo, ou string vazia se inválido."""
    if pd.isna(cod):
        return ""
    c = str(cod).replace(".0", "").strip()
    if not c or c.upper() == "NAN" or c == "0000000000" or c == "0":
        return ""
    return c.zfill(10)

def extrair_escala_plantao(arquivo_escala) -> dict:
    """
    Retorna um dicionário onde a chave é a DATA (YYYY-MM-DD)
    e o valor é uma lista de nomes normalizados dos médicos escalados no dia.
    """
    escala = {}
    df = pd.read_excel(arquivo_escala, sheet_name=None, header=None, engine="openpyxl")
    
    for nome_aba, ws in df.items():
        if nome_aba.lower().startswith('plan'):
            continue
            
        datas_colunas = {} 
        for idx, row in ws.iterrows():
            tem_data = False
            for col_idx, val in enumerate(row):
                if pd.isna(val):
                    continue
                # Identifica a data
                if isinstance(val, datetime):
                    datas_colunas[col_idx] = val.strftime("%Y-%m-%d")
                    tem_data = True
                elif isinstance(val, str) and ("2026-" in val or "2025-" in val or "2024-" in val):
                    try:
                        d = pd.to_datetime(val)
                        datas_colunas[col_idx] = d.strftime("%Y-%m-%d")
                        tem_data = True
                    except:
                        pass
            
            if tem_data:
                continue
                
            # Ler médicos nas colunas que têm data mapeada
            for col_idx, val in enumerate(row):
                if col_idx in datas_colunas and pd.notna(val):
                    medico = normalizar_nome(val)
                    if medico and len(medico) > 3 and medico not in ["SD", "SN", "MANHA", "TARDE", "UTI - 6H"]:
                        data_plantao = datas_colunas[col_idx]
                        if data_plantao not in escala:
                            escala[data_plantao] = []
                        escala[data_plantao].append(medico)
                        
    return escala

def medico_na_escala(data_str: str, nome_medico: str, escala_dict: dict) -> bool:
    """Verifica se o médico bate com a escala usando intersecção de nomes."""
    if not data_str or not nome_medico:
        return False
        
    medico_norm = normalizar_nome(nome_medico)
    if not medico_norm:
        return False
        
    partes_medico = set(medico_norm.split())
    primeiro_nome_medico = medico_norm.split()[0]
    
    escalados_no_dia = escala_dict.get(data_str, [])
    for escalado in escalados_no_dia:
        partes_escalado = set(escalado.split())
        if not partes_escalado:
            continue
            
        primeiro_nome_escalado = escalado.split()[0]
        
        # O primeiro nome precisa ser idêntico
        if primeiro_nome_medico != primeiro_nome_escalado:
            continue
            
        # Pelo menos o primeiro nome e mais um sobrenome devem bater
        palavras_em_comum = partes_medico.intersection(partes_escalado)
        if len(palavras_em_comum) >= 2:
            return True
            
        # Fallback: se o nome da escala estiver totalmente contido no relatório
        if escalado in medico_norm or medico_norm in escalado:
            return True
            
    return False

# ===============================================
# REGRAS DO MODELO 01 (HGCA)
# ===============================================
def validar_linha_hgca(row: dict, dict_sigtap: dict, escala_dict: dict) -> list:
    status = []
    
    cod = normalizar_codigo(row.get("codigo_sigtap"))
    if not cod:
        return [] # Ignora linha se não tiver código válido
        
    desc = str(row.get("descritivo", "")).upper()
    if "TOTAL" in desc:
        return []

    # 1. Validação CBO
    if cod not in dict_sigtap:
        status.append("CÓDIGO FORA DO CBO")
    else:
        valor_tabela = dict_sigtap[cod]
        valor_cobrado = formatar_moeda(row.get("valor_sp"))
        if abs(valor_cobrado - valor_tabela) > TOLERANCIA_CENTAVOS:
            status.append(f"VALOR DIVERGENTE (Tabela: R$ {valor_tabela:.2f})")

    # 2. Validação de Escala
    data_raw = row.get("data_cirurgia")
    data_str = ""
    if isinstance(data_raw, datetime):
        data_str = data_raw.strftime("%Y-%m-%d")
    elif isinstance(data_raw, str):
        try:
            data_str = pd.to_datetime(data_raw).strftime("%Y-%m-%d")
        except:
            pass
            
    medico = row.get("profissional")
    # np.nan é 'truthy', então garantimos que seja string válida e não-nula
    if data_str and pd.notna(medico) and str(medico).strip():
        if not medico_na_escala(data_str, str(medico), escala_dict):
            status.append("CIRURGIÃO NÃO ESCALADO NO DIA")

    if not status:
        status.append("OK")
        
    return status

# ===============================================
# REGRAS DO MODELO 02 (HGC)
# ===============================================
def validar_linha_hgc(row: dict, dict_sigtap: dict, escala_dict: dict) -> list:
    status = []
    
    cod = normalizar_codigo(row.get("codigo_sigtap"))
    if not cod:
        return []
        
    valor_proc = formatar_moeda(row.get("valor_proc"))
    valor_princ = formatar_moeda(row.get("valor_princ"))
    valor_aux = formatar_moeda(row.get("valor_aux"))
    
    medico_princ = str(row.get("cirurgiao", ""))
    medico_aux = str(row.get("auxiliar", ""))
    
    data_raw = row.get("data")
    data_str = ""
    if isinstance(data_raw, datetime):
        data_str = data_raw.strftime("%Y-%m-%d")
    elif isinstance(data_raw, str):
        try:
            data_str = pd.to_datetime(data_raw, dayfirst=True).strftime("%Y-%m-%d")
        except:
            pass

    # 1. Validação CBO e Valor Tabela
    if cod not in dict_sigtap:
        status.append("CÓDIGO FORA DO CBO")
    else:
        valor_tabela = dict_sigtap[cod]
        if abs(valor_proc - valor_tabela) > TOLERANCIA_CENTAVOS:
            status.append(f"VALOR BASE DIVERGENTE (Tabela: R$ {valor_tabela:.2f})")

    # 2. Rateio 75%
    calc_75 = valor_proc * 0.75
    if abs(valor_princ - calc_75) > TOLERANCIA_CENTAVOS:
        status.append(f"75% INCORRETO (Esp: R$ {calc_75:.2f})")

    # 3. Rateio 25% e Auxiliar
    nome_aux_norm = normalizar_nome(medico_aux)
    tem_auxiliar = bool(nome_aux_norm) and nome_aux_norm not in ["NAO CONSTA", "NENHUM"]
    
    if tem_auxiliar:
        calc_25 = valor_proc * 0.25
        if abs(valor_aux - calc_25) > TOLERANCIA_CENTAVOS:
            status.append(f"25% INCORRETO (Esp: R$ {calc_25:.2f})")
    else:
        if valor_aux > 0:
            status.append("25% FATURADO SEM AUXILIAR")

    # 4. Escala (Presença do Principal e Auxiliar)
    if data_str:
        if medico_princ and not medico_na_escala(data_str, medico_princ, escala_dict):
            status.append("PRINCIPAL NÃO ESCALADO NO DIA")
        if tem_auxiliar and not medico_na_escala(data_str, medico_aux, escala_dict):
            status.append("AUXILIAR NÃO ESCALADO NO DIA")

    if not status:
        status.append("OK")
        
    return status
