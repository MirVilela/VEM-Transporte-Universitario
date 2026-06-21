import urllib.request
import urllib.error
import sys

routes = [
    ("/", "index.html"),
    ("/gestora", "gestora.html"),
    ("/motorista", "motorista.html")
]

BASE_URL = "http://127.0.0.1:5000"

print("Iniciando verificação de rotas de Frontend...")

for path, name in routes:
    url = BASE_URL + path
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                html = response.read().decode('utf-8')
                # Check for the new CSS variable
                if "--accent: #f39c12;" in html:
                    print(f"[OK] {name} carregado com sucesso (HTTP 200) e contém o novo CSS.")
                else:
                    print(f"[AVISO] {name} carregou, mas não encontrou o novo CSS.")
            else:
                print(f"[ERRO] {name} falhou com status {response.status}")
    except Exception as e:
        print(f"[ERRO] {name} falhou: {str(e)}")
