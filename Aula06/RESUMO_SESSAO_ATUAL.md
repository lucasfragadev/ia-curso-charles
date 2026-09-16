# Resumo do Projeto: Sistema de Auditoria SUS (Fase Aula06)

## 📌 Contexto e Objetivos
Construímos a nova versão do motor de auditoria de faturamento SUS, focada em cruzar dados de produção hospitalar com a **Tabela SIGTAP** e a **Escala de Plantões Médicos**. O sistema foi dividido para suportar as regras de dois hospitais com modelos de negócios diferentes:
- **Modelo 01 (HGCA):** Validação de códigos SIGTAP e checagem de presença na escala do dia.
- **Modelo 02 (HGC):** Validação de códigos SIGTAP, checagem de presença na escala, e validação de rateio financeiro (75% Cirurgião Principal / 25% Médico Auxiliar).

## 🏗️ Arquitetura e Arquivos Criados
O sistema foi refatorado para seguir boas práticas de Engenharia de Software (Test-Driven Development - TDD, Funções Puras, Separação de Responsabilidades).

1. **`Aula06/auditoria_core.py`** (O Cérebro)
   - Contém apenas as "leis" da auditoria. 
   - Recebe dicionários/dados em memória e retorna listas de erros (status).
   - **Inteligência de Nomes:** Usa teoria de intersecção de conjuntos (Sets). Para aprovar um médico na escala, o primeiro nome deve ser idêntico e eles devem ter pelo menos um sobrenome em comum, ignorando abreviações e "FILHO/NETO".
   - **Tratamento de Dados:** Trata adequadamente células vazias (`NaN`) geradas pelo Pandas, evitando falsos positivos de "Código Fora do CBO".

2. **`Aula06/test_auditoria.py`** (A Garantia de Qualidade)
   - Suíte de testes automatizados rodando via `pytest`.
   - Simula cenários reais sem precisar carregar planilhas pesadas, cobrindo:
     - Erros de digitação em nomes.
     - Médico operando fora do dia de plantão.
     - Erros matemáticos (rateio de 75/25 cobrado incorretamente).
     - Ignorar OPME e linhas de TOTAL.

3. **`Aula06/auditoria_escala.py`** (O Executor)
   - Script principal que deve ser executado no terminal.
   - Lê os arquivos Excel físicos (`docs/1- AGOSTO...`, `docs/PLANILHA AGOSTO HGC...` e a base SIGTAP).
   - Passa os dados para o `core` e exporta relatórios organizados na pasta `auditoria/YYYY-MM-DD/` com abas separadas para "Divergências".

## 🚀 Como Executar (Comandos para o Terminal)

Para rodar o sistema e gerar os relatórios em Excel:
```bash
.venv\Scripts\python.exe "C:\Users\lucasaf\Documents\pessoal\ia-curso-charles\Aula06\auditoria_escala.py"
```

Para rodar os testes de qualidade (Garantia de que as regras de negócio não foram quebradas):
```bash
.venv\Scripts\pytest.exe "C:\Users\lucasaf\Documents\pessoal\ia-curso-charles\Aula06\test_auditoria.py"
```

## 💡 Próximos Passos (Para a próxima sessão)
- Extrair automaticamente o extrato em PDF (IBC) ou encontrar forma de injetar os dados de produtividade da "parcela fixa" (Eixo A do HGCA).
- Atualizar o arquivo `.bat` (`build.bat`) que empacota o software usando o PyInstaller, de forma a englobar esse novo motor num arquivo `.exe` executável para os usuários finais.
