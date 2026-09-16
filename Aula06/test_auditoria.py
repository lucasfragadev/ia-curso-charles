import pytest
import pandas as pd
from datetime import datetime
from auditoria_core import (
    normalizar_codigo, 
    normalizar_nome, 
    medico_na_escala,
    validar_linha_hgca,
    validar_linha_hgc
)

def test_normalizar_codigo():
    assert normalizar_codigo("403010144") == "0403010144"
    assert normalizar_codigo(403010144) == "0403010144"
    assert normalizar_codigo("0403010144") == "0403010144"
    assert normalizar_codigo("NAN") == ""
    assert normalizar_codigo(pd.NA) == ""
    assert normalizar_codigo(None) == ""
    assert normalizar_codigo("0000000000") == ""
    assert normalizar_codigo(0) == ""

def test_normalizar_nome():
    assert normalizar_nome("  JoÃo dE soUZa  ") == "JOAO DE SOUZA"
    assert normalizar_nome(pd.NA) == ""
    
def test_medico_na_escala():
    escala = {
        "2026-08-01": ["EDUARDO VARJAO VIEIRA", "WAGNER HERCULANO", "JAQUISSON GUIMARAES", "LUIZ SOEIRO"],
        "2026-08-02": ["CAMILA MOURA", "ARTUR BASTOS"]
    }
    
    # Médico que está na escala, com nome ligeiramente diferente
    assert medico_na_escala("2026-08-01", "EDUARDO VARJÃO", escala) == True
    # Médico que NÃO está na escala do dia 1
    assert medico_na_escala("2026-08-01", "ARTUR BASTOS", escala) == False
    # Médico que está na escala no dia 2
    assert medico_na_escala("2026-08-02", "ARTUR BASTOS", escala) == True
    # Nome complexo com "FILHO" no final (Caso real)
    assert medico_na_escala("2026-08-01", "JAQUISSON  DE DEUS GUIMARÃES FILHO", escala) == True
    # Nome complexo do Soeiro
    assert medico_na_escala("2026-08-01", "LUIZ AUGUSTO MEDRADO SOEIRO", escala) == True
    
def test_validar_linha_hgca_ok():
    row = {
        "codigo_sigtap": "0403010144",
        "descritivo": "Reconstrução craniana",
        "valor_sp": "671.94",
        "data_cirurgia": "2026-08-01",
        "profissional": "WAGNER HERCULANO"
    }
    sigtap = {"0403010144": 671.94}
    escala = {"2026-08-01": ["WAGNER HERCULANO"]}
    
    status = validar_linha_hgca(row, sigtap, escala)
    assert status == ["OK"]

def test_validar_linha_hgca_total_ignorado():
    row = {
        "codigo_sigtap": "",
        "descritivo": "TOTAL",
        "valor_sp": "1200.00"
    }
    assert validar_linha_hgca(row, {}, {}) == []

def test_validar_linha_hgca_erros():
    row = {
        "codigo_sigtap": "99999",
        "valor_sp": "100.0",
        "data_cirurgia": "2026-08-01",
        "profissional": "DR ESTRANHO"
    }
    sigtap = {"0403010144": 671.94}
    escala = {"2026-08-01": ["WAGNER HERCULANO"]}
    
    status = validar_linha_hgca(row, sigtap, escala)
    assert "CÓDIGO FORA DO CBO" in status
    assert "CIRURGIÃO NÃO ESCALADO NO DIA" in status

def test_validar_linha_hgc_erros_rateio():
    row = {
        "codigo_sigtap": "0403010144",
        "valor_proc": "1000.00",
        "valor_princ": "700.00",  # Errado, deveria ser 750
        "valor_aux": "300.00",    # Errado, deveria ser 250
        "cirurgiao": "WAGNER",
        "auxiliar": "CAMILA",
        "data": "2026-08-01"
    }
    sigtap = {"0403010144": 1000.00}
    escala = {"2026-08-01": ["WAGNER", "CAMILA"]}
    
    status = validar_linha_hgc(row, sigtap, escala)
    assert "75% INCORRETO (Esp: R$ 750.00)" in status
    assert "25% INCORRETO (Esp: R$ 250.00)" in status

def test_validar_linha_hgc_25_por_cento_sem_auxiliar():
    row = {
        "codigo_sigtap": "0403010144",
        "valor_proc": "1000.00",
        "valor_princ": "750.00",  
        "valor_aux": "250.00",    
        "cirurgiao": "WAGNER",
        "auxiliar": "NÃO CONSTA", # Faturou o 25% mas não tem nome
        "data": "2026-08-01"
    }
    sigtap = {"0403010144": 1000.00}
    escala = {"2026-08-01": ["WAGNER"]}
    
    status = validar_linha_hgc(row, sigtap, escala)
    assert "25% FATURADO SEM AUXILIAR" in status
