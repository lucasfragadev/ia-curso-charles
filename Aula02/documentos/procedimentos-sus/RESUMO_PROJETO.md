# Contexto do Projeto: Automação SIGTAP (Instituto do Cérebro)

Este documento serve como um "ponto de salvamento" (brain dump) do projeto. Ele contém toda a lógica, descobertas técnicas e estrutura desenvolvida até o momento, ideal para ser compartilhado com qualquer IA para retomar o trabalho exatamente de onde paramos.

## 1. Regras do Usuário (Instituto do Cérebro)
- **NOME:** O usuário deve ser SEMPRE chamado de **Instituto do Cérebro**.
- **AUTORIZAÇÃO:** Antes de iniciar a execução de novos scripts demorados ou aplicar novos comandos que alterem a estrutura, a IA DEVE explicar o cenário e perguntar se pode prosseguir.
- **CLEAN CODE:** O código deve seguir princípios SOLID (responsabilidades separadas) e ser altamente organizado.

## 2. Objetivo Geral do Projeto
Automatizar a extração e validação de procedimentos médicos do **SIGTAP (DATASUS)** via API SOAP, cruzando esses dados com planilhas manuais de faturamento hospitalar para fins de **Auditoria**. O foco inicial está em procedimentos vinculados a CBOs específicos (ex: 225260 - Neurocirurgião).

## 3. Estrutura de Pastas Atual
```text
procedimentos-sus/
├── docs/                 # Documentações da API e planilhas originais de controle (ex: planilha da Letícia)
├── data/                 # Planilhas de entrada/saída de dados puros (.xlsx)
├── auditoria/            # Relatórios finais de cruzamento (organizados por data: YYYY-MM-DD)
├── .venv/                # Ambiente virtual Python (requer requests, pandas, openpyxl)
├── src/                  # Código-fonte Python isolado
│   ├── config.py                          # Constantes, credenciais e configurações de CBO
│   ├── sigtap_client.py                   # Lógica isolada de requisições SOAP (com retry)
│   ├── xml_parser.py                      # Lógica isolada de extração de tags do XML retornado
│   ├── extrair_todos_procedimentos.py     # Baixa toda a base geral do DATASUS
│   ├── filtrar_por_cbo.py                 # Filtra a base geral validando quais procedimentos aceitam o CBO alvo
│   ├── buscar_valores_procedimentos.py    # Enriquecimento: busca valores (SA, SH, SP) de uma lista de procedimentos
│   └── auditoria_modelo01.py              # Script final de cruzamento (Modelo 01)
└── RESUMO_PROJETO.md     # Este arquivo
```

## 4. Descobertas Técnicas Críticas (O que a IA precisa saber sobre a API)
- **Endpoint SOAP:** `https://servicos.saude.gov.br/sigtap/ProcedimentoService/v1`
- **Autenticação:** WS-Security no Header. Usuário: `SIGTAP.PUBLICO`, Senha: `sigtap#2015public`.
- **Competência:** O uso da tag `<com:competencia>201501</com:competencia>` é obrigatório em várias requisições para que a API não retorne Erro 500.
- **Códigos SIGTAP (10 dígitos):** Ferramentas como Excel/Pandas tendem a remover os zeros à esquerda (ex: `0408030291` vira `408030291`). É OBRIGATÓRIO forçar a leitura como string e aplicar `.zfill(10)` sempre que for consultar a API, senão a requisição falha.
- **Valores Financeiros:** Os valores do SUS (`valorSA`, `valorSH`, `valorSP`) NÃO vêm no endpoint básico `pesquisarProcedimentos`. Para obtê-los, é preciso usar o endpoint `detalharProcedimento` com alguma categoria adicional exigida (usamos `DESCRICAO` para ser mais leve). Os valores vêm soltos no XML de resposta dentro de `<ns6:Procedimento>`.

## 5. Status Atual e Próximos Passos
- **Concluído:** Extração massiva, filtro de procedimentos apenas para o CBO 225260 (Neurocirurgião), enriquecimento financeiro (adicionando os valores em Reais da tabela SUS).
- **Concluído:** Criação do **Conferência-Modelo01**, que cruza uma planilha de controle humano ("Planilha da Letícia") com a base da verdade da API, detectando divergências de valores no centavo e apontando procedimentos não autorizados para o CBO.
- **Próximos Passos (Amanhã):** Desenvolver novos formatos de cruzamento ("Modelo 02", etc.) dependendo das novas planilhas ou novos CBOs (ex: Neurologista Clínico) que o Instituto do Cérebro enviar.
