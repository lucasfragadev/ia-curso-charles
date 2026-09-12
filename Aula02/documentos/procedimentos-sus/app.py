"""
AuditoriaSUS - Servidor Local

Ponto de entrada do executavel. Inicia um servidor HTTP local,
abre o navegador automaticamente e serve a interface HTML para o usuario.

Nao requer instalacao de Flask ou qualquer dependencia externa —
utiliza apenas modulos da biblioteca padrao do Python.
"""
# Imports explícitos para garantir que o PyInstaller empacote
# openpyxl e suas dependências corretamente no .exe
import openpyxl                      # noqa: F401
import openpyxl.styles               # noqa: F401
import openpyxl.utils                # noqa: F401
import openpyxl.writer.excel         # noqa: F401
import openpyxl.reader.excel         # noqa: F401
import et_xmlfile                    # noqa: F401
import pandas as pd                  # noqa: F401 — força bundle no .exe e usado em _analisar_planilha

import json
import os
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# =====================================================================
# Configuracao de caminhos (compativel com PyInstaller)
# =====================================================================

if getattr(sys, 'frozen', False):
    # Rodando como .exe gerado pelo PyInstaller
    BASE_DIR = os.path.dirname(sys.executable)
    TEMPLATES_DIR = os.path.join(sys._MEIPASS, 'templates')
else:
    # Rodando como script Python normal
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

# Garante que os caminhos relativos (data/, auditoria/) apontem
# para a mesma pasta onde o executavel esta
os.chdir(BASE_DIR)

# Adiciona o diretorio raiz ao sys.path para permitir imports de src.*
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.auditoria_modelo01 import executar as executar_modelo01
from src.auditoria_modelo02 import executar as executar_modelo02
from src.config import CBO_NEUROCIRURGIAO

# =====================================================================
# Configuracao de porta
# =====================================================================
HOST = "127.0.0.1"
PORTA_PREFERIDA = 5050


def encontrar_porta_livre() -> int:
    """
    Tenta usar a porta preferida (5050).
    Se estiver ocupada (ex: instancia anterior ainda rodando),
    encontra automaticamente outra porta livre no sistema.
    """
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, PORTA_PREFERIDA))
            return PORTA_PREFERIDA
        except OSError:
            # Porta ocupada — pede ao SO uma porta livre qualquer
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
                s2.bind((HOST, 0))
                return s2.getsockname()[1]


# =====================================================================
# Handler HTTP
# =====================================================================

class AuditoriaHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/':
            self._servir_html()
        elif parsed.path == '/escolher-arquivo':
            self._escolher_arquivo()
        elif parsed.path == '/analisar-planilha':
            self._analisar_planilha()
        elif parsed.path == '/abrir-relatorio':
            params = parse_qs(parsed.query)
            caminho = params.get('path', [''])[0]
            self._abrir_relatorio(caminho)
        else:
            self._resposta_json({"erro": "Rota nao encontrada."}, status=404)

    def do_POST(self):
        if self.path == '/executar':
            self._executar_auditoria()
        else:
            self._resposta_json({"erro": "Rota nao encontrada."}, status=404)

    # ------------------------------------------------------------------
    # Rotas
    # ------------------------------------------------------------------

    def _servir_html(self):
        """Serve a pagina principal da interface."""
        index_path = os.path.join(TEMPLATES_DIR, 'index.html')
        try:
            with open(index_path, 'rb') as f:
                conteudo = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(conteudo)
        except FileNotFoundError:
            self._resposta_json({"erro": f"index.html nao encontrado em: {index_path}"}, status=500)

    def _escolher_arquivo(self):
        """
        Abre a janela nativa do Windows para selecionar um arquivo .xlsx.
        Usa tkinter (embutido no Python) — sem dependencias externas.
        """
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            caminho = filedialog.askopenfilename(
                title="Selecionar Planilha Excel",
                filetypes=[("Planilhas Excel", "*.xlsx *.xls"), ("Todos os arquivos", "*.*")]
            )
            root.destroy()
            self._resposta_json({"path": caminho or ""})
        except Exception as e:
            self._resposta_json({"erro": str(e)}, status=500)

    def _analisar_planilha(self):
        """
        Le os cabecalhos reais da planilha selecionada e retorna a lista de colunas.
        O front-end usa essa lista para popular os dropdowns de mapeamento.
        """
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        caminho = params.get('path', [''])[0]
        modelo  = params.get('modelo', [''])[0]

        if not caminho or not os.path.exists(caminho):
            self._resposta_json({"sucesso": False, "erro": "Arquivo nao encontrado."})
            return

        try:
            # Detecta o cabeçalho dinamicamente
            df_temp = pd.read_excel(caminho, header=None, nrows=25, engine='openpyxl')
            best_row = 0
            max_score = 0
            for idx, row in df_temp.iterrows():
                row_str = ' '.join([str(val).upper() for val in row.values if pd.notna(val)])
                score = 0
                if 'SIGTAP' in row_str: score += 5
                if 'VALOR' in row_str: score += 2
                if 'PACIENTE' in row_str: score += 2
                if 'CÓD' in row_str or 'COD' in row_str: score += 2
                if score > max_score:
                    max_score = score
                    best_row = idx

            # Carrega a linha de cabeçalho correta
            df = pd.read_excel(caminho, header=best_row, nrows=0, engine='openpyxl')

            colunas = [str(c) for c in df.columns.tolist() if not str(c).startswith('Unnamed')]
            self._resposta_json({"sucesso": True, "colunas": colunas, "linha_cabecalho": best_row})
        except Exception as e:
            self._resposta_json({"sucesso": False, "erro": f"Erro ao ler planilha: {str(e)}"})

    def _executar_auditoria(self):
        """Executa o modelo de auditoria selecionado e retorna o resultado."""
        try:
            tamanho = int(self.headers.get('Content-Length', 0))
            corpo   = self.rfile.read(tamanho)
            dados   = json.loads(corpo.decode('utf-8'))

            modelo          = dados.get('modelo', '')
            planilha        = dados.get('planilha', '').strip()
            cbo             = dados.get('cbo', CBO_NEUROCIRURGIAO).strip() or CBO_NEUROCIRURGIAO
            mapeamento      = dados.get('mapeamento', None)
            linha_cabecalho = dados.get('linha_cabecalho', None)

            if not planilha:
                self._resposta_json({"sucesso": False, "erro": "Nenhuma planilha foi selecionada."})
                return

            if not os.path.exists(planilha):
                self._resposta_json({"sucesso": False, "erro": f"Arquivo nao encontrado: {planilha}"})
                return

            if modelo == '01':
                resultado = executar_modelo01(planilha, cbo, mapeamento, linha_cabecalho)
            elif modelo == '02':
                resultado = executar_modelo02(planilha, cbo, mapeamento, linha_cabecalho)
            else:
                self._resposta_json({"sucesso": False, "erro": "Modelo invalido. Selecione Modelo 01 ou Modelo 02."})
                return

            self._resposta_json(resultado)

        except Exception as e:
            self._resposta_json({"sucesso": False, "erro": f"Erro inesperado: {str(e)}"}, status=500)

    def _abrir_relatorio(self, caminho: str):
        """Abre o arquivo de relatorio no programa padrao (Excel)."""
        try:
            if caminho and os.path.exists(caminho):
                os.startfile(caminho)
                self._resposta_json({"ok": True})
            else:
                self._resposta_json({"erro": "Arquivo nao encontrado."}, status=404)
        except Exception as e:
            self._resposta_json({"erro": str(e)}, status=500)

    # ------------------------------------------------------------------
    # Utilitarios
    # ------------------------------------------------------------------

    def _resposta_json(self, dados: dict, status: int = 200):
        conteudo = json.dumps(dados, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(conteudo)

    def log_message(self, format, *args):
        """Suprime os logs de acesso do servidor no console."""
        pass


# =====================================================================
# Inicializacao
# =====================================================================

def iniciar_servidor(porta: int):
    servidor = HTTPServer((HOST, porta), AuditoriaHandler)
    servidor.serve_forever()


def main():
    porta = encontrar_porta_livre()

    print("=" * 50)
    print("  AuditoriaSUS - Instituto do Cerebro")
    print("=" * 50)
    print(f"  Diretorio de trabalho : {BASE_DIR}")
    print(f"  Servidor iniciando    : http://{HOST}:{porta}")
    if porta != PORTA_PREFERIDA:
        print(f"  (porta {PORTA_PREFERIDA} ocupada — usando {porta} automaticamente)")
    print("  Pressione Ctrl+C para encerrar.")
    print("=" * 50)

    # Inicia o servidor em background (thread daemon encerra junto com o processo)
    thread = threading.Thread(target=iniciar_servidor, args=(porta,), daemon=True)
    thread.start()

    # Abre o navegador apos um breve instante para o servidor subir
    threading.Timer(0.8, lambda: webbrowser.open(f"http://{HOST}:{porta}")).start()

    # Mantem o processo principal vivo
    try:
        thread.join()
    except KeyboardInterrupt:
        print("\n  Encerrando servidor...")


if __name__ == "__main__":
    main()
