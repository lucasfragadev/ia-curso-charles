
## Escala de Faturamento x Extrato / Relatório de Faturamento enviado pela unidade

### Precisamos verificar se a ESCALA enviada foi utilizada corretamente para gerar o Relatório de Faturamento (Parte fixa).

Verificar itens a seguir:

- Médicos escalados  
- Data
- Turno (SD, SN, Manhã ou Tarde)
- Função (Plantonista, Diarista - 6h, Coordenador - 6h, Ambulatório - 6h);


### Relatório de Faturamento enviado pela unidade x Produtividade referido mês

-- Médicos executantes (Se estão no mesmo dia, se possuem turno em comum (SN ou SD, Manhã ou Tarde));
-- Data da cirurgia

-----

# MANUAL TÉCNICO DE AUDITORIA HOSPITALAR E CONFERÊNCIA DE FATURAMENTO
**Prestador:** Instituto Baiano do Cérebro (IBC)  
**Especialidades:** Neurocirurgia / Neurofisiologia Clínica / Otorrinolaringologia  
**Competência Base:** Mensal (Exemplo de referência: Agosto/2026)

---

## 1. DISTINÇÃO FUNDAMENTAL DE UNIDADES E MODELOS DE AUDITORIA

As análises envolvem duas unidades hospitalares estaduais totalmente distintas, cada uma regida por seu próprio contrato, estrutura de faturamento e modelo operacional:

| Característica | Unidade 1: HGCA (Feira de Santana) | Unidade 2: HGC (Camaçari) |
|---|---|---|
| **Hospital** | Hospital Geral Clériston Andrade | Hospital Geral de Camaçari |
| **Padrão no Sistema** | **Modelo 01** | **Modelo 02** |
| **Arquivo de Produtividade** | `1- AGOSTO NEUROCIRURGIA 2026 - HOSPITAL` | `PLANILHA AGOSTO HGC` |
| **Formato de Cirurgias** | Relatório de atos cirúrgicos por paciente e cirurgião executante | Planilha analítica com cálculo de rateio (75% Principal / 25% Auxiliar) |
| **Auditoria de Parte Fixa** | Sim, via Extrato Mensal SESAB (`IBC.pdf`) confrontado com Escala HGCA | Realizada conforme extrato/escala específicos do HGC |

> **Nota:** Os arquivos do HGCA e do HGC são independentes e não se comunicam. Cada unidade possui sua própria base de auditoria.

---

## 2. AUDITORIA HGCA — HOSPITAL GERAL CLÉRISTON ANDRADE (MODELO 01)

### 2.1. Eixo A: Auditoria da Parcela Fixa (Escala HGCA x Extrato Mensal SESAB)
* **Origem (Planejamento):** `ESCALA NEUROCIRURGIA AGOSTO 2026- FATURAMENTO` (Abas `NEUROCIRURGIA` - CT 063/2025 e `261-2025` - CT 261/2025).
* **Destino (Faturamento do Hospital):** `IBC.pdf` (Extrato Mensal gerado pelo HGCA/SESAB).

#### Regras de Validação:
1. **Identificação Nominal e Vínculo:**
   - Conferência de Nome e CPF do profissional.
   - Validação da especialidade e do contrato administrativo correspondente.
2. **Conferência Temporal e Turnos:**
   - Batimento estrito da **Data** (dia do mês).
   - Batimento do **Turno**:
     - `SD` (Plantão Diurno - 12h: 07h às 19h).
     - `SN` (Plantão Noturno - 12h: 19h às 07h).
     - `Manhã` / `Tarde` (Turnos parciais de 6h).
3. **Mapeamento de Carga Horária e Cargo/Função:**
   - Na escala, os serviços são distribuídos por setor e carga horária (Coluna `SERVIÇO-CH` da escala: `EMERGÊNCIA - 12H`, `ENFERMARIA - 12H`, `ENFERMARIA - 6H`, `UTI - 6H`, etc.).
   - No extrato (`IBC.pdf`), esses serviços são liquidados em categorias funcionais contratuais:
     - `PLANTONISTA`: Plantões de 12h (SD/SN em Emergência ou Enfermaria).
     - `DIARISTA - 6H`: Cargas diárias de 6h (Manhã ou Tarde em UTI/Enfermaria).
     - `AMBULATÓRIO - 6H`: Atendimentos ambulatoriais de 6h.
     - `COORDENADOR - 6H`: Horas de coordenação técnica e rotina.
4. **Apuração de Inconformidades:**
   - 🔴 **Glosa:** Turno faturado no extrato sem correspondente na escala (plantão não autorizado).
   - 🟡 **Substituição:** Divergência entre o médico escalado e o médico que faturou (necessidade de espelho de troca).
   - 🔴 **Incompatibilidade:** Registro concomitante do mesmo médico em dois turnos ou locais sobrepostos.

### 2.2. Eixo B: Auditoria da Produtividade Cirúrgica HGCA
* **Base:** Relatório emitido por Contas Hospitalares do HGCA (`1- AGOSTO NEUROCIRURGIA 2026 - HOSPITAL`).
* **Regras de Validação:**
  1. Identificação de cada ato cirúrgico: Paciente, Registro Hospitalar, Data da Cirurgia e Código SIGTAP.
  2. **Presença em Escala:** Confirmar se o **Profissional executante** indicado no relatório estava em escala ativa no HGCA na data da cirurgia.
  3. **Conferência de Tabela:** Validação do `Valor SP SIGTAP` cobrado frente à Tabela da Verdade SIGTAP oficial (CBO 225260).

---

## 3. AUDITORIA HGC — HOSPITAL GERAL DE CAMAÇARI (MODELO 02)

### 3.1. Eixo: Auditoria da Produtividade e Rateio Cirúrgico
* **Base:** Planilha analítica de produtividade do HGC (`PLANILHA AGOSTO HGC`, aba `HGC PROD AGOSTO 2026 `).

#### Regras de Validação:
1. **Conferência de Procedimentos e Valores SIGTAP:**
   - Validar se o `CÓDIGO SIGTAP` é previsto para o CBO de Neurocirurgia (225260).
   - Validar se o `VALOR DO PROCEDIMENTO` lançado confere com a Tabela Oficial SIGTAP (coluna `valorSP`).
2. **Auditoria de Rateio da Equipe (75% / 25%):**
   - **Cirurgião Principal:** Deve receber exatamente **75%** do valor do procedimento.
   - **Médico Auxiliar:** Deve receber exatamente **25%** do valor do procedimento quando houver auxiliar lançado.
   - Se constar `NÃO CONSTA` no auxiliar, o valor de 25% não deve ser faturado como auxiliar (ou segue regra de procedimento sem auxiliar).
   - Tolerância máxima de centavos por arredondamento: R$ 0,05.
3. **Auditoria de Equipe Executante e Turno Comum:**
   - **Turno e Data:** A planilha registra a `DATA DO PROCEDIMENTO` e o `TURNO` (ex.: SD).
   - **Validação Cruzada com a Escala do HGC:** 
     - Verificar se o **Cirurgião Principal** e o **Médico Auxiliar** estavam escalados e em atividade no hospital na **mesma data**.
     - Confirmar se ambos possuíam **turno em comum** (ambos em plantão SD ou ambos em SN), assegurando a legitimidade da atuação cirúrgica conjunta.

---

## 4. DIRETRIZES TÉCNICAS PARA O DESENVOLVIMENTO DO NOVO SCRIPT

O novo script automatizado deverá estruturar as conferências respeitando essa clara segregação:

1. **Módulo 1 — HGCA (Clériston Andrade):**
   - Conciliação automática de Parcela Fixa: Leitura do Extrato (`IBC.pdf`) x Leitura da Escala HGCA (Data, Turno, Médico, Carga Horária).
   - Conferência de cirurgias do HGCA: confrontar atos cirúrgicos com a presença dos cirurgiões em escala.
2. **Módulo 2 — HGC (Camaçari):**
   - Validação dos procedimentos SIGTAP e percentuais de 75% e 25%.
   - Cruzamento da equipe (Cirurgião Principal x Auxiliar) com a escala do HGC para validação de data e turno coincidente.
3. **Relatórios Finais de Auditoria:**
   - Emissão de relatórios em Excel com status claro para cada linha (`Conforme`, `Divergente`, `Não Previsto`, `Equipe Incompatível`).