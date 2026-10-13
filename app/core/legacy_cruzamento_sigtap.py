"""
Cruzamento de dados entre planilha local e API SIGTAP.

Le uma planilha com codigos de procedimentos, consulta a API para
verificar se pertencem a uma especialidade (via CBO) e gera uma
planilha de resultado com status OK/SINALIZADO.

Uso:
    python -m src.cruzamento_sigtap
    python -m src.cruzamento_sigtap --cbo 225260
"""
import argparse
import os
import time
import pandas as pd

from src.config import (
    CBO_NEUROLOGISTA,
    ARQUIVO_PLANILHA_ENTRADA,
    ARQUIVO_RESULTADO,
    PAUSA_ENTRE_PAGINAS,
)
from src.sigtap_client import detalhar_procedimento
from src.xml_parser import procedimento_possui_cbo


def main():
    parser = argparse.ArgumentParser(description="Cruzamento de planilha com API SIGTAP")
    parser.add_argument("--cbo", default=CBO_NEUROLOGISTA,
                        help=f"Codigo CBO para verificar (default: {CBO_NEUROLOGISTA} - Neurologista)")
    parser.add_argument("--entrada", default=ARQUIVO_PLANILHA_ENTRADA,
                        help="Planilha de entrada")
    parser.add_argument("--saida", default=ARQUIVO_RESULTADO,
                        help="Planilha de saida")
    parser.add_argument("--coluna", default="codigo",
                        help="Nome da coluna com codigos dos procedimentos")
    args = parser.parse_args()

    print("=" * 60, flush=True)
    print(f"  Cruzamento SIGTAP - CBO: {args.cbo}", flush=True)
    print("=" * 60 + "\n", flush=True)

    if not os.path.exists(args.entrada):
        print(f"[!] Planilha '{args.entrada}' nao encontrada.", flush=True)
        print(f"    Criando exemplo com dados fictcios...", flush=True)
        os.makedirs(os.path.dirname(args.entrada), exist_ok=True)
        pd.DataFrame({args.coluna: ["0203010027", "0303010011"]}).to_excel(args.entrada, index=False)

    df = pd.read_excel(args.entrada)

    if args.coluna not in df.columns:
        print(f"Erro: Coluna '{args.coluna}' nao encontrada. Colunas disponiveis: {list(df.columns)}", flush=True)
        return

    status_lista = []

    for idx, row in df.iterrows():
        codigo = str(row[args.coluna]).strip().zfill(10)
        print(f"  [{idx + 1}/{len(df)}] Analisando: {codigo}", flush=True)

        xml_resp = detalhar_procedimento(codigo)

        if xml_resp and procedimento_possui_cbo(xml_resp, args.cbo):
            status_lista.append("OK")
            print(f"    -> OK (CBO {args.cbo} encontrado)", flush=True)
        else:
            status_lista.append("SINALIZADO")

        time.sleep(PAUSA_ENTRE_PAGINAS)

    df["status"] = status_lista
    os.makedirs(os.path.dirname(args.saida), exist_ok=True)
    df.to_excel(args.saida, index=False)
    print(f"\nSucesso! Resultado salvo em '{args.saida}'.", flush=True)


if __name__ == "__main__":
    main()
