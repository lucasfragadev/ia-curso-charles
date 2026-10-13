import xml.etree.ElementTree as ET


def extrair_procedimentos(xml_text: str) -> list[dict]:
    """Extrai lista de {codigo, descricao} dos blocos BaseProcedimento."""
    procedimentos = []
    root = ET.fromstring(xml_text)

    for parent in root.iter():
        if parent.tag.split("}")[-1] == "BaseProcedimento":
            codigo = None
            nome = None
            for child in parent:
                tag = child.tag.split("}")[-1]
                if tag == "codigo":
                    codigo = child.text
                elif tag == "nome":
                    nome = child.text
            if codigo and nome:
                procedimentos.append({"codigo": codigo, "descricao": nome})

    return procedimentos


def extrair_total_registros(xml_text: str) -> int:
    """Extrai o campo totalRegistros da paginacao da resposta."""
    root = ET.fromstring(xml_text)
    for elem in root.iter():
        if elem.tag.split("}")[-1] == "totalRegistros" and elem.text:
            try:
                return int(elem.text)
            except ValueError:
                pass
    return 0


def extrair_cbos(xml_text: str) -> list[dict]:
    """Extrai lista de {codigo, nome} dos CBOs retornados por detalharProcedimento."""
    cbos = []
    root = ET.fromstring(xml_text)

    current_code = None
    for elem in root.iter():
        tag = elem.tag.split("}")[-1]
        if tag == "codigo" and elem.text and len(elem.text.strip()) == 6:
            current_code = elem.text.strip()
        elif tag == "nome" and elem.text and current_code:
            cbos.append({"codigo": current_code, "nome": elem.text})
            current_code = None

    return cbos


def procedimento_possui_cbo(xml_text: str, cbo_alvo: str) -> bool:
    """Verifica se um CBO especifico esta vinculado ao procedimento."""
    cbos = extrair_cbos(xml_text)
    return any(cbo["codigo"] == cbo_alvo for cbo in cbos)


def extrair_valores(xml_text: str) -> dict:
    """Extrai os valores financeiros (SA, SH, SP) do XML detalhado."""
    valores = {"valorSA": 0.0, "valorSH": 0.0, "valorSP": 0.0}
    
    if not xml_text:
        return valores
        
    try:
        root = ET.fromstring(xml_text)
        for elem in root.iter():
            tag = elem.tag.split("}")[-1]
            if tag in ["valorSA", "valorSH", "valorSP"] and elem.text:
                try:
                    valores[tag] = float(elem.text)
                except ValueError:
                    pass
    except ET.ParseError:
        pass
        
    return valores
