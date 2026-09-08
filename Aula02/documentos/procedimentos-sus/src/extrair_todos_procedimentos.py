"""
Extracao completa de todos os procedimentos da tabela SIGTAP.

Varre todos os grupos (01-09) com paginacao automatica e salva
o resultado em uma planilha Excel.

Uso:
    python -m src.extrair_todos_procedimentos
"""
import time
import pandas as pd

from src.config import GRUPOS, REGISTROS_POR_PAGINA, PAUSA_ENTRE_PAGINAS, ARQUIVO_TODOS_PROCEDIMENTOS
from src.sigtap_client import pesquisar_procedimentos
from src.xml_parser import extrair_procedimentos, extrair_total_registros


def extrair_grupo(grupo: str) -> list[dict]:
    """Extrai todos os procedimentos de um grupo com paginacao automatica."""
    procedimentos = []
    registro_inicial = 1
    total_registros = None

    while True:
        print(f"  -> Buscando registros {registro_inicial} a "
              f"{registro_inicial + REGISTROS_POR_PAGINA - 1}...", flush=True)

        xml_resp = pesquisar_procedimentos(grupo, registro_inicial)

        if xml_resp is None:
            print(f"  -> Falha apos todas as tentativas. Pulando grupo {grupo}.", flush=True)
            break

        procs = extrair_procedimentos(xml_resp)

        if total_registros is None:
            total_registros = extrair_total_registros(xml_resp)
            print(f"  -> Total de registros no grupo {grupo}: {total_registros}", flush=True)

        if not procs:
            break

        procedimentos.extend(procs)
        registro_inicial += REGISTROS_POR_PAGINA

        if total_registros and registro_inicial > total_registros:
            break

        time.sleep(PAUSA_ENTRE_PAGINAS)

    return procedimentos


def main():
    print("=" * 60, flush=True)
    print("  Extracao total de Procedimentos do SIGTAP (DATASUS)", flush=True)
    print("=" * 60 + "\n", flush=True)

    todos = []

    for grupo in GRUPOS:
        print(f"[Grupo {grupo}] Iniciando varredura...", flush=True)
        procs = extrair_grupo(grupo)
        todos.extend(procs)
        print(f"[Grupo {grupo}] Concluido! Extraidos: {len(procs)}\n", flush=True)

    if not todos:
        print("Nenhum procedimento encontrado.", flush=True)
        return

    df = pd.DataFrame(todos).drop_duplicates(subset=["codigo"])
    df.to_excel(ARQUIVO_TODOS_PROCEDIMENTOS, index=False)
    print(f"Sucesso! {len(df)} procedimentos salvos em '{ARQUIVO_TODOS_PROCEDIMENTOS}'.", flush=True)


if __name__ == "__main__":
    main()
