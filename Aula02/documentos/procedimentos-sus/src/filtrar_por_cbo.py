"""
Filtra procedimentos por CBO (especialidade) usando a API SIGTAP.

Le a planilha de todos os procedimentos ja extraidos, consulta os CBOs
de cada um via API e gera uma nova planilha apenas com os procedimentos
vinculados ao CBO informado.

Uso:
    python -m src.filtrar_por_cbo
    python -m src.filtrar_por_cbo --cbo 225260
    python -m src.filtrar_por_cbo --cbo 225112 --saida data/neurologista.xlsx
"""
import argparse
import time
import pandas as pd

from src.config import (
    CBO_NEUROCIRURGIAO,
    ARQUIVO_TODOS_PROCEDIMENTOS,
    PAUSA_ENTRE_PAGINAS,
)
from src.sigtap_client import detalhar_procedimento
from src.xml_parser import procedimento_possui_cbo, extrair_cbos


def filtrar_procedimentos_por_cbo(df: pd.DataFrame, cbo_alvo: str) -> pd.DataFrame:
    """Consulta a API para cada procedimento e marca se possui o CBO alvo.

    Adiciona as colunas:
        - possui_cbo: True/False
        - status: 'OK' ou 'SINALIZADO'
    """
    resultados = []
    total = len(df)

    for idx, row in df.iterrows():
        codigo = str(row["codigo"]).strip().zfill(10)
        descricao = row.get("descricao", "")
        print(f"  [{idx + 1}/{total}] {codigo} - {descricao}", flush=True)

        xml_resp = detalhar_procedimento(codigo)

        if xml_resp is None:
            print(f"    -> Falha ao detalhar. Marcando como SINALIZADO.", flush=True)
            resultados.append({"possui_cbo": False, "status": "SINALIZADO", "cbos_vinculados": ""})
            continue

        possui = procedimento_possui_cbo(xml_resp, cbo_alvo)
        cbos = extrair_cbos(xml_resp)
        cbos_str = "; ".join(f"{c['codigo']}-{c['nome']}" for c in cbos)

        status = "OK" if possui else "SINALIZADO"
        if possui:
            print(f"    -> CBO {cbo_alvo} ENCONTRADO!", flush=True)

        resultados.append({
            "possui_cbo": possui,
            "status": status,
            "cbos_vinculados": cbos_str,
        })

        time.sleep(PAUSA_ENTRE_PAGINAS)

    df_resultado = df.copy()
    df_resultado["possui_cbo"] = [r["possui_cbo"] for r in resultados]
    df_resultado["status"] = [r["status"] for r in resultados]
    df_resultado["cbos_vinculados"] = [r["cbos_vinculados"] for r in resultados]

    return df_resultado


def main():
    parser = argparse.ArgumentParser(description="Filtra procedimentos SIGTAP por CBO")
    parser.add_argument("--cbo", default=CBO_NEUROCIRURGIAO,
                        help=f"Codigo CBO sem hifen (default: {CBO_NEUROCIRURGIAO} - Neurocirurgiao)")
    parser.add_argument("--entrada", default=ARQUIVO_TODOS_PROCEDIMENTOS,
                        help="Planilha de entrada com todos os procedimentos")
    parser.add_argument("--saida", default=None,
                        help="Planilha de saida (default: data/procedimentos_cbo_<CBO>.xlsx)")
    args = parser.parse_args()

    arquivo_saida = args.saida or f"data/procedimentos_cbo_{args.cbo}.xlsx"

    print("=" * 60, flush=True)
    print(f"  Filtragem de Procedimentos por CBO: {args.cbo}", flush=True)
    print("=" * 60 + "\n", flush=True)

    print(f"Lendo planilha de entrada: {args.entrada}", flush=True)
    df = pd.read_excel(args.entrada)
    print(f"Total de procedimentos para analisar: {len(df)}\n", flush=True)

    df_resultado = filtrar_procedimentos_por_cbo(df, args.cbo)

    # Salvar resultado completo
    df_resultado.to_excel(arquivo_saida, index=False)

    # Estatisticas
    total_ok = df_resultado["status"].value_counts().get("OK", 0)
    total_sinalizado = df_resultado["status"].value_counts().get("SINALIZADO", 0)

    print(f"\n{'=' * 60}", flush=True)
    print(f"  Resultado:", flush=True)
    print(f"    Procedimentos com CBO {args.cbo}: {total_ok}", flush=True)
    print(f"    Procedimentos sem CBO {args.cbo}: {total_sinalizado}", flush=True)
    print(f"  Salvo em: {arquivo_saida}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
