"""
Configuracoes centralizadas do projeto SIGTAP.

Principio: Single Responsibility - este modulo cuida exclusivamente
de constantes e configuracoes, sem logica de negocio.
"""

# =====================================================================
# API
# =====================================================================
URL_PROCEDIMENTO_SERVICE = "https://servicos.saude.gov.br/sigtap/ProcedimentoService/v1"
URL_NIVEL_AGREGACAO_SERVICE = "https://servicos.saude.gov.br/sigtap/NivelAgregacaoService/v1"

SOAP_HEADERS = {"Content-Type": "application/soap+xml; charset=utf-8"}

# Credenciais publicas do SIGTAP (conforme documentacao oficial)
SIGTAP_USUARIO = "SIGTAP.PUBLICO"
SIGTAP_SENHA = "sigtap#2015public"

# =====================================================================
# Parametros de consulta
# =====================================================================
COMPETENCIA = "201501"
GRUPOS = ["01", "02", "03", "04", "05", "06", "07", "08", "09"]

# Paginacao
REGISTROS_POR_PAGINA = 20
MAX_TENTATIVAS = 3

# =====================================================================
# Timeouts (em segundos)
# =====================================================================
TIMEOUT_REQUISICAO = 60
PAUSA_ENTRE_PAGINAS = 0.3
PAUSA_APOS_ERRO = 2
PAUSA_APOS_TIMEOUT = 3

# =====================================================================
# CBOs de interesse
# =====================================================================
CBO_NEUROLOGISTA = "225112"
CBO_NEUROCIRURGIAO = "225260"

# =====================================================================
# Caminhos de arquivos (relativos ao diretorio raiz do projeto)
# =====================================================================
PASTA_DADOS = "data"
ARQUIVO_TODOS_PROCEDIMENTOS = "data/todos_procedimentos_sigtap.xlsx"
ARQUIVO_PLANILHA_ENTRADA = "data/minha_planilha.xlsx"
ARQUIVO_RESULTADO = "data/resultado.xlsx"
