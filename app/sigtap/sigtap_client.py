"""
Cliente SOAP para comunicacao com a API SIGTAP do DATASUS.

Principio: Single Responsibility - este modulo encapsula toda a
comunicacao HTTP/SOAP com a API, incluindo autenticacao, montagem
de envelopes XML e logica de retry.
"""
import time
import requests
from src.config import (
    URL_PROCEDIMENTO_SERVICE,
    SOAP_HEADERS,
    SIGTAP_USUARIO,
    SIGTAP_SENHA,
    COMPETENCIA,
    REGISTROS_POR_PAGINA,
    MAX_TENTATIVAS,
    TIMEOUT_REQUISICAO,
    PAUSA_APOS_ERRO,
    PAUSA_APOS_TIMEOUT,
)


def _auth_header() -> str:
    """Retorna o bloco WS-Security para autenticacao SOAP."""
    return f"""<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
      <wsse:UsernameToken wsu:Id="Id-0001334008436683-000000002c4a1908-1" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
        <wsse:Username>{SIGTAP_USUARIO}</wsse:Username>
        <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{SIGTAP_SENHA}</wsse:Password>
      </wsse:UsernameToken>
    </wsse:Security>"""


def _post_soap(xml_body: str) -> requests.Response | None:
    """Executa um POST SOAP com retry automatico.

    Returns:
        Response em caso de sucesso (HTTP 200), None em caso de falha.
    """
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            response = requests.post(
                URL_PROCEDIMENTO_SERVICE,
                data=xml_body,
                headers=SOAP_HEADERS,
                timeout=TIMEOUT_REQUISICAO,
            )
            if response.status_code == 200:
                return response

            print(f"    [Tentativa {tentativa}/{MAX_TENTATIVAS}] HTTP {response.status_code}", flush=True)
            time.sleep(PAUSA_APOS_ERRO)

        except requests.exceptions.Timeout:
            print(f"    [Tentativa {tentativa}/{MAX_TENTATIVAS}] Timeout", flush=True)
            time.sleep(PAUSA_APOS_TIMEOUT)

        except Exception as e:
            print(f"    [Tentativa {tentativa}/{MAX_TENTATIVAS}] Erro: {e}", flush=True)
            time.sleep(PAUSA_APOS_ERRO)

    return None


def pesquisar_procedimentos(grupo: str, registro_inicial: int,
                            quantidade: int = REGISTROS_POR_PAGINA) -> str | None:
    """Busca procedimentos paginados por grupo.

    Returns:
        XML de resposta como string, ou None em caso de falha.
    """
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
xmlns:proc="http://servicos.saude.gov.br/sigtap/v1/procedimentoservice"
xmlns:grup="http://servicos.saude.gov.br/schema/sigtap/procedimento/nivelagregacao/v1/grupo"
xmlns:com="http://servicos.saude.gov.br/schema/corporativo/v1/competencia"
xmlns:pag="http://servicos.saude.gov.br/wsdl/mensageria/v1/paginacao">
  <soap:Header>{_auth_header()}</soap:Header>
  <soap:Body>
    <proc:requestPesquisarProcedimentos>
      <grup:codigoGrupo>{grupo}</grup:codigoGrupo>
      <com:competencia>{COMPETENCIA}</com:competencia>
      <pag:Paginacao>
        <pag:registroInicial>{registro_inicial}</pag:registroInicial>
        <pag:quantidadeRegistros>{quantidade}</pag:quantidadeRegistros>
        <pag:totalRegistros>0</pag:totalRegistros>
      </pag:Paginacao>
    </proc:requestPesquisarProcedimentos>
  </soap:Body>
</soap:Envelope>"""

    resp = _post_soap(xml)
    return resp.text if resp else None


def detalhar_procedimento(codigo_procedimento: str,
                          categoria_detalhe: str = "CBOS",
                          quantidade_cbos: int = 20) -> str | None:
    """Busca os detalhes vinculados a um procedimento.

    Returns:
        XML de resposta como string, ou None em caso de falha.
    """
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
xmlns:proc="http://servicos.saude.gov.br/sigtap/v1/procedimentoservice"
xmlns:proc1="http://servicos.saude.gov.br/schema/sigtap/procedimento/v1/procedimento"
xmlns:det="http://servicos.saude.gov.br/wsdl/mensageria/sigtap/v1/detalheadicional"
xmlns:pag="http://servicos.saude.gov.br/wsdl/mensageria/v1/paginacao">
  <soap:Header>{_auth_header()}</soap:Header>
  <soap:Body>
    <proc:requestDetalharProcedimento>
      <proc1:codigoProcedimento>{codigo_procedimento}</proc1:codigoProcedimento>
      <proc:DetalhesAdicionais>
        <det:DetalheAdicional>
          <det:categoriaDetalheAdicional>{categoria_detalhe}</det:categoriaDetalheAdicional>
          <det:Paginacao>
            <pag:registroInicial>1</pag:registroInicial>
            <pag:quantidadeRegistros>{quantidade_cbos}</pag:quantidadeRegistros>
            <pag:totalRegistros>0</pag:totalRegistros>
          </det:Paginacao>
        </det:DetalheAdicional>
      </proc:DetalhesAdicionais>
    </proc:requestDetalharProcedimento>
  </soap:Body>
</soap:Envelope>"""

    resp = _post_soap(xml)
    return resp.text if resp else None
