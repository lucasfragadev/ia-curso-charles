# procedimentos-sus/
# Projeto de automacao para cruzamento de dados com a API SIGTAP (DATASUS)
#
# Estrutura:
#   docs/              -> Documentacao de referencia (PDF, .http)
#   data/              -> Planilhas de entrada e saida
#   src/               -> Codigo-fonte do projeto
#     config.py        -> Constantes e configuracoes centralizadas
#     sigtap_client.py -> Cliente SOAP para comunicacao com a API SIGTAP
#     xml_parser.py    -> Parser de respostas XML da API
#     extrair_todos_procedimentos.py  -> Script de extracao completa
#     filtrar_por_cbo.py              -> Script de filtragem por CBO (ex: Neurocirurgiao)
#     cruzamento_sigtap.py            -> Script de cruzamento com planilha local
#   .venv/             -> Ambiente virtual Python
#   requirements.txt   -> Dependencias do projeto
