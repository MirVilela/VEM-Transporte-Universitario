"""
Verificacao completa do ambiente Python para o Projeto VEM (SPTU).
Execute: python verify_env.py
"""
import sys
import importlib.metadata

def check():
    print("=" * 55)
    print("  Verificacao Completa do Ambiente Python - Projeto VEM")
    print("=" * 55)
    print()

    # [1] Python
    print(f"[1] Python:    {sys.version.split()[0]}")
    print(f"    Exec:      {sys.executable}")
    print()

    # [2] Flask e dependencias
    flask_v = importlib.metadata.version("flask")
    werkzeug_v = importlib.metadata.version("werkzeug")
    jinja2_v = importlib.metadata.version("jinja2")
    print(f"[2] Flask:     {flask_v} ... OK")
    print(f"    Werkzeug:  {werkzeug_v} ... OK")
    print(f"    Jinja2:    {jinja2_v} ... OK")
    print()

    # [3-8] Biblioteca padrao
    import sqlite3
    print(f"[3] SQLite:    {sqlite3.sqlite_version} ... OK")

    import json
    print("[4] json:      OK")

    import os
    print("[5] os:        OK")

    import hashlib
    print("[6] hashlib:   OK")

    import datetime
    print("[7] datetime:  OK")

    import logging
    print("[8] logging:   OK")

    print()

    # Teste rapido do Flask
    from flask import Flask
    app = Flask(__name__)

    @app.route("/health")
    def health():
        return {"status": "ok"}

    with app.test_client() as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        print("[9] Flask test_client /health -> 200 OK")

    # Teste rapido do SQLite
    import sqlite3 as sq
    conn = sq.connect(":memory:")
    conn.execute("CREATE TABLE teste (id TEXT PRIMARY KEY, valor TEXT)")
    conn.execute("INSERT INTO teste VALUES ('1', 'VEM')")
    row = conn.execute("SELECT valor FROM teste WHERE id='1'").fetchone()
    assert row[0] == "VEM"
    conn.close()
    print("[10] SQLite in-memory CRUD -> OK")

    print()
    print("=" * 55)
    print("  >>> Todos os modulos necessarios estao funcionando!")
    print("=" * 55)


if __name__ == "__main__":
    try:
        check()
    except Exception as e:
        print(f"\n[ERRO] {e}")
        sys.exit(1)
