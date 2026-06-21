"""
app.py — Motor Backend do Sistema Preditivo de Transporte Universitario (SPTU)
Framework: Flask 3.x | Banco: SQLite 3 | Metodologia: VEM (Karpathy-style)

Rotas de API conforme SCHEMA.md (JSON is Law):
  POST /api/login          — Autenticacao CPF + PIN
  POST /api/reservar       — Registrar reservas da semana
  GET  /api/semana         — Consultar semana do aluno
  GET  /api/painel         — Painel da gestora (X-Admin-Token)
  GET  /api/checklist/<d>  — Lista do motorista (X-Admin-Token)
  POST /api/checkin        — Confirmar embarque (X-Admin-Token)
  GET  /api/veiculos       — Listar frota (X-Admin-Token)
  POST /api/veiculos       — Adicionar veiculo (X-Admin-Token)
  PUT  /api/veiculos/<id>  — Editar veiculo (X-Admin-Token)
  DELETE /api/veiculos/<id>— Remover veiculo (X-Admin-Token)
  GET  /api/passageiros    — Listar passageiros (X-Admin-Token)
  POST /api/passageiros    — Cadastrar passageiro (X-Admin-Token)
  DELETE /api/passageiros/<cpf> — Excluir passageiro (X-Admin-Token)
  GET  /api/configuracoes  — Ler configuracoes (X-Admin-Token)
  PUT  /api/configuracoes  — Atualizar configuracoes (X-Admin-Token)
  GET  /api/status-inscricoes — Status atual das inscricoes
  GET  /api/server-time    — Hora do servidor (UTC)
  --- Requisito A: Mural de Avisos ---
  GET  /api/avisos         — Listar avisos ativos (Publico/WhatsApp-ready)
  POST /api/avisos         — Criar aviso (X-Admin-Token)
  PUT  /api/avisos/<id>    — Editar aviso (X-Admin-Token)
  DELETE /api/avisos/<id>  — Arquivar aviso (X-Admin-Token)
  --- Requisito B: Status de Viagem ---
  GET  /api/pontos-rota    — Listar pontos de rota (X-Admin-Token)
  POST /api/pontos-rota    — Cadastrar ponto (X-Admin-Token)
  DELETE /api/pontos-rota/<id> — Remover ponto (X-Admin-Token)
  PUT  /api/status-viagem  — Motorista atualiza posicao (X-Admin-Token)
  GET  /api/status-viagem/<data> — Consultar status do dia (Publico/WhatsApp-ready)

Execucao: python app.py
"""

import os
import sys
import sqlite3
import hashlib
import json
import logging
import time
from datetime import datetime, date, timedelta, timezone
from flask import Flask, request, jsonify, send_from_directory

# Tentar importar zoneinfo (Python 3.9+)
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Fallback para backports se necessario
    try:
        from backports.zoneinfo import ZoneInfo
    except ImportError:
        ZoneInfo = None

# ══════════════════════════════════════════════
# CONFIGURACAO (Caminhos Absolutos — 04-BACKEND_GUIDE.md)
# ══════════════════════════════════════════════

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
STATIC_DIR = os.path.join(BASE_DIR, "static")

ADMIN_TOKEN = "vem-admin-2026"
HARD_LOCK_HOUR = 14  # RS03: Fallback caso nao haja config no banco
SERVER_TIMEZONE = "America/Sao_Paulo"

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout
)
log = logging.getLogger("VEM")


# ══════════════════════════════════════════════
# BANCO DE DADOS (SQLite — SCHEMA.md "The Law")
# ══════════════════════════════════════════════

def get_db():
    """Conexao com row_factory para dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def hash_pin(pin):
    """Hash SHA-256 do PIN."""
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()


def init_db():
    """Cria tabelas conforme SCHEMA.md (RS02: sem auto-incremento)."""
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS alunos (
            cpf         TEXT PRIMARY KEY,
            nome        TEXT NOT NULL,
            pin         TEXT NOT NULL,
            rota        TEXT NOT NULL,
            tipo_vaga   TEXT DEFAULT 'NORMAL',
            ativo       INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS reservas (
            id          TEXT PRIMARY KEY,
            cpf         TEXT NOT NULL REFERENCES alunos(cpf),
            data        TEXT NOT NULL,
            ida         INTEGER DEFAULT 0,
            volta       INTEGER DEFAULT 0,
            status      TEXT DEFAULT 'ATIVA',
            criado_em   TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS veiculos (
            id          TEXT PRIMARY KEY,
            nome        TEXT DEFAULT '',
            tipo        TEXT NOT NULL,
            capacidade  INTEGER NOT NULL,
            ativo       INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS checkins (
            id              TEXT PRIMARY KEY,
            cpf             TEXT NOT NULL REFERENCES alunos(cpf),
            veiculo_id      TEXT NOT NULL REFERENCES veiculos(id),
            data            TEXT NOT NULL,
            tipo            TEXT NOT NULL,
            confirmado_em   TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS configuracoes (
            chave   TEXT PRIMARY KEY,
            valor   TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS avisos (
            id          TEXT PRIMARY KEY,
            titulo      TEXT NOT NULL,
            mensagem    TEXT NOT NULL,
            tipo        TEXT DEFAULT 'INFO',
            criado_em   TEXT DEFAULT (datetime('now')),
            expira_em   TEXT,
            ativo       INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS rotas (
            id      TEXT PRIMARY KEY,
            nome    TEXT NOT NULL,
            ativo   INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS pontos_rota (
            id      TEXT PRIMARY KEY,
            rota_id TEXT NOT NULL REFERENCES rotas(id),
            nome    TEXT NOT NULL,
            ordem   INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS status_viagem (
            id              TEXT PRIMARY KEY,
            veiculo_id      TEXT NOT NULL REFERENCES veiculos(id),
            data            TEXT NOT NULL,
            tipo            TEXT NOT NULL,
            ponto_atual_id  TEXT,
            status          TEXT DEFAULT 'AGUARDANDO',
            atualizado_em   TEXT DEFAULT (datetime('now'))
        );
    """)

    # ── Migracao: adicionar coluna 'nome' em veiculos se nao existir ──
    try:
        cur.execute("SELECT nome FROM veiculos LIMIT 1")
    except sqlite3.OperationalError:
        cur.execute("ALTER TABLE veiculos ADD COLUMN nome TEXT DEFAULT ''")
        log.info("Migracao: coluna 'nome' adicionada a tabela veiculos")

    # ── Seed: dados de teste (mesmo mock do index.html) ──
    seed_alunos = [
        ("12345678901", "Joao Silva",     hash_pin("1234"), "Cidade A -> Campus", "NORMAL"),
        ("98765432100", "Maria Souza",    hash_pin("5678"), "Cidade B -> Campus", "EXCECAO"),
        ("11122233344", "Carlos Oliveira", hash_pin("0000"), "Cidade A -> Campus", "NORMAL"),
    ]
    for a in seed_alunos:
        cur.execute(
            "INSERT OR IGNORE INTO alunos (cpf, nome, pin, rota, tipo_vaga) VALUES (?,?,?,?,?)", a
        )

    seed_veiculos = [
        ("ONIBUS-01", "Onibus Escolar 01", "ONIBUS", 44),
        ("ONIBUS-02", "Onibus Escolar 02", "ONIBUS", 44),
        ("MICRO-01",  "Micro Universitario", "MICRO",  28),
        ("VAN-01",    "Van Executiva",      "VAN",    15),
    ]
    for v in seed_veiculos:
        cur.execute(
            "INSERT OR IGNORE INTO veiculos (id, nome, tipo, capacidade) VALUES (?,?,?,?)", v
        )

    # ── Seed: configuracoes padrao ──
    seed_config = [
        ("horario_corte", "14:00"),
        ("trava_manual", "AUTO"),
        ("limite_avisos", "10"),
    ]
    for c in seed_config:
        cur.execute(
            "INSERT OR IGNORE INTO configuracoes (chave, valor) VALUES (?,?)", c
        )

    # ── Seed: rotas de exemplo ──
    seed_rotas = [
        ("ROTA-CIDADEA", "Cidade A -> Campus"),
        ("ROTA-CIDADEB", "Cidade B -> Campus")
    ]
    for r in seed_rotas:
        cur.execute(
            "INSERT OR IGNORE INTO rotas (id, nome) VALUES (?,?)", r
        )

    # ── Seed: pontos de rota de exemplo ──
    seed_pontos = [
        ("PR-CIDADEA-1", "ROTA-CIDADEA", "Saida Garagem", 1),
        ("PR-CIDADEA-2", "ROTA-CIDADEA", "Rodoviaria", 2),
        ("PR-CIDADEA-3", "ROTA-CIDADEA", "Ponto Central", 3),
        ("PR-CIDADEA-4", "ROTA-CIDADEA", "Campus (Chegada)", 4),
        ("PR-CIDADEB-1", "ROTA-CIDADEB", "Saida Garagem", 1),
        ("PR-CIDADEB-2", "ROTA-CIDADEB", "Terminal", 2),
        ("PR-CIDADEB-3", "ROTA-CIDADEB", "Campus (Chegada)", 3),
    ]
    for p in seed_pontos:
        cur.execute(
            "INSERT OR IGNORE INTO pontos_rota (id, rota_id, nome, ordem) VALUES (?,?,?,?)", p
        )

    conn.commit()
    conn.close()
    log.info("DB inicializado em %s", DB_PATH)


# ══════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════

def require_admin():
    """Valida X-Admin-Token (04-BACKEND_GUIDE.md §4)."""
    token = request.headers.get("X-Admin-Token", "")
    if token != ADMIN_TOKEN:
        return jsonify({"sucesso": False, "erro": "Token administrativo invalido"}), 403
    return None


def get_server_now():
    """Retorna datetime 'agora' no fuso do servidor (America/Sao_Paulo).
    Lida corretamente com horario de verao e anos bissextos."""
    utc_now = datetime.now(timezone.utc)
    if ZoneInfo:
        try:
            return utc_now.astimezone(ZoneInfo(SERVER_TIMEZONE))
        except Exception:
            # Fallback se tzdata nao estiver instalado (Windows)
            pass
    # Fallback: UTC-3 fixo (Brasilia padrao)
    return utc_now.astimezone(timezone(timedelta(hours=-3)))


def get_config(chave, fallback=None):
    """Le uma configuracao do banco."""
    conn = get_db()
    row = conn.execute("SELECT valor FROM configuracoes WHERE chave=?", (chave,)).fetchone()
    conn.close()
    return row["valor"] if row else fallback


def is_hard_locked(data_str):
    """RS03: Verifica se a data esta bloqueada.
    Respeita: (1) trava manual, (2) horario de corte dinamico, (3) fuso correto."""

    try:
        data_reserva = date.fromisoformat(data_str)
    except ValueError:
        return False

    agora = get_server_now()
    hoje = agora.date()

    # Nao permitir reserva para dias que ja passaram, independente da trava
    if data_reserva < hoje:
        return True

    # 1. Verificar trava manual (override)
    trava = get_config("trava_manual", "AUTO")
    if trava == "FECHADO":
        return True
    if trava == "ABERTO":
        return False

    # 2. Logica normal com horario de corte dinamico
    horario_str = get_config("horario_corte", "14:00")
    try:
        partes = horario_str.split(":")
        hora_corte = int(partes[0])
        minuto_corte = int(partes[1]) if len(partes) > 1 else 0
    except (ValueError, IndexError):
        hora_corte = HARD_LOCK_HOUR
        minuto_corte = 0

    if data_reserva == hoje:
        hora_atual = agora.hour
        minuto_atual = agora.minute
        if (hora_atual > hora_corte) or (hora_atual == hora_corte and minuto_atual >= minuto_corte):
            return True

    return False


def sugerir_frota(total_passageiros):
    """RN03: Calcula combinacao de veiculos para minimizar ociosidade."""
    conn = get_db()
    veiculos = conn.execute(
        "SELECT tipo, capacidade FROM veiculos WHERE ativo=1 ORDER BY capacidade DESC"
    ).fetchall()
    conn.close()

    capacidades = {}
    for v in veiculos:
        tipo = v["tipo"]
        if tipo not in capacidades:
            capacidades[tipo] = v["capacidade"]

    # Ordem: ONIBUS (44) > MICRO (28) > VAN (15)
    ordem = [("ONIBUS", capacidades.get("ONIBUS", 44)),
             ("MICRO",  capacidades.get("MICRO", 28)),
             ("VAN",    capacidades.get("VAN", 15))]

    resultado = []
    restante = total_passageiros
    for tipo, cap in ordem:
        if restante <= 0:
            break
        qtd = restante // cap
        if qtd > 0:
            resultado.append({"tipo": tipo, "qtd": qtd})
            restante -= qtd * cap

    # Sobra — encaixar no menor veiculo que comporte
    if restante > 0:
        for tipo, cap in reversed(ordem):
            if cap >= restante:
                melhor = (tipo, 1)
        # fallback
        if restante > 0:
            tipo_f, _ = melhor if 'melhor' in dir() else (ordem[-1][0], 1)
            # Verificar se ja existe no resultado
            encontrou = False
            for item in resultado:
                if item["tipo"] == tipo_f:
                    item["qtd"] += 1
                    encontrou = True
                    break
            if not encontrou:
                resultado.append({"tipo": tipo_f, "qtd": 1})

    return resultado


# ══════════════════════════════════════════════
# ROTAS — FRONTEND (Servir static/)
# ══════════════════════════════════════════════

@app.route("/")
def serve_index():
    log.info("Servindo index.html")
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/gestora")
def serve_gestora():
    log.info("Servindo gestora.html")
    return send_from_directory(STATIC_DIR, "gestora.html")


@app.route("/motorista")
def serve_motorista():
    log.info("Servindo motorista.html")
    return send_from_directory(STATIC_DIR, "motorista.html")


# ══════════════════════════════════════════════
# ROTAS — API (SCHEMA.md §3 "JSON is Law")
# ══════════════════════════════════════════════

@app.route("/api/login", methods=["POST"])
def api_login():
    """Autenticacao CPF + PIN (RF01, RS01)."""
    dados = request.get_json(silent=True) or {}
    cpf = str(dados.get("cpf", "")).strip()
    pin = str(dados.get("pin", "")).strip()

    if len(cpf) != 11 or not cpf.isdigit():
        return jsonify({"sucesso": False, "erro": "CPF invalido"}), 400

    if len(pin) != 4 or not pin.isdigit():
        return jsonify({"sucesso": False, "erro": "PIN invalido"}), 400

    conn = get_db()
    aluno = conn.execute("SELECT * FROM alunos WHERE cpf=? AND ativo=1", (cpf,)).fetchone()
    conn.close()

    if not aluno or aluno["pin"] != hash_pin(pin):
        log.info("Login FALHOU para CPF %s", cpf)
        return jsonify({"sucesso": False, "erro": "CPF ou PIN incorretos"}), 401

    log.info("Login OK: %s (CPF: %s)", aluno["nome"], cpf)
    return jsonify({
        "sucesso": True,
        "aluno": {
            "cpf": aluno["cpf"],
            "nome": aluno["nome"],
            "rota": aluno["rota"],
            "tipo_vaga": aluno["tipo_vaga"]
        }
    })


@app.route("/api/reservar", methods=["POST"])
def api_reservar():
    """Registrar reservas semanais (RF02, RS03 Hard Lock)."""
    dados = request.get_json(silent=True) or {}
    cpf = str(dados.get("cpf", "")).strip()
    lista = dados.get("reservas", [])

    if not cpf or not lista:
        return jsonify({"sucesso": False, "erro": "Dados incompletos"}), 400

    conn = get_db()
    aluno = conn.execute("SELECT cpf FROM alunos WHERE cpf=? AND ativo=1", (cpf,)).fetchone()
    if not aluno:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Aluno nao encontrado"}), 404

    total = 0
    for r in lista:
        data_str = str(r.get("data", ""))
        ida = int(r.get("ida", 0))
        volta = int(r.get("volta", 0))

        if not data_str:
            continue
        if ida == 0 and volta == 0:
            continue
        if is_hard_locked(data_str):
            log.info("Hard Lock: reserva bloqueada para %s", data_str)
            continue

        reserva_id = f"{cpf}_{data_str}"
        conn.execute("""
            INSERT INTO reservas (id, cpf, data, ida, volta, status, criado_em)
            VALUES (?, ?, ?, ?, ?, 'ATIVA', datetime('now'))
            ON CONFLICT(id) DO UPDATE SET ida=?, volta=?, status='ATIVA', criado_em=datetime('now')
        """, (reserva_id, cpf, data_str, ida, volta, ida, volta))
        total += 1

    conn.commit()
    conn.close()

    log.info("Reservas salvas: %d dias para CPF %s", total, cpf)
    return jsonify({
        "sucesso": True,
        "mensagem": "Reservas da semana registradas com sucesso.",
        "total_registradas": total
    })


@app.route("/api/semana", methods=["GET"])
def api_semana():
    """Consultar reservas da semana do aluno."""
    cpf = request.args.get("cpf", "").strip()
    if not cpf:
        return jsonify({"sucesso": False, "erro": "CPF obrigatorio"}), 400

    dias_nome = {0: "Segunda", 1: "Terca", 2: "Quarta", 3: "Quinta", 4: "Sexta"}

    conn = get_db()
    rows = conn.execute(
        "SELECT data, ida, volta, status FROM reservas WHERE cpf=? AND status='ATIVA' ORDER BY data",
        (cpf,)
    ).fetchall()
    conn.close()

    semana = []
    for row in rows:
        try:
            d = date.fromisoformat(row["data"])
            dia_nome = dias_nome.get(d.weekday(), "")
        except ValueError:
            dia_nome = ""
        semana.append({
            "data": row["data"],
            "dia": dia_nome,
            "ida": row["ida"],
            "volta": row["volta"],
            "status": row["status"]
        })

    return jsonify({"semana": semana})


@app.route("/api/painel", methods=["GET"])
def api_painel():
    """Painel da gestora com volumetria e sugestao de frota (RF03)."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    conn = get_db()
    rows = conn.execute("""
        SELECT
            r.data,
            SUM(r.ida) as total_ida,
            SUM(r.volta) as total_volta,
            SUM(CASE WHEN a.tipo_vaga='EXCECAO' AND r.ida=1 THEN 1 ELSE 0 END) as excecoes_ida,
            SUM(CASE WHEN a.tipo_vaga='EXCECAO' AND r.volta=1 THEN 1 ELSE 0 END) as excecoes_volta
        FROM reservas r
        JOIN alunos a ON r.cpf = a.cpf
        WHERE r.status = 'ATIVA'
        GROUP BY r.data
        ORDER BY r.data
    """).fetchall()
    conn.close()

    dias_nome = {0: "Segunda", 1: "Terca", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sabado", 6: "Domingo"}
    resumo = []
    for row in rows:
        try:
            d = date.fromisoformat(row["data"])
            dia_nome = dias_nome.get(d.weekday(), "")
        except ValueError:
            dia_nome = ""

        total_ida = row["total_ida"] or 0
        total_volta = row["total_volta"] or 0

        resumo.append({
            "data": row["data"],
            "dia": dia_nome,
            "total_ida": total_ida,
            "total_volta": total_volta,
            "excecoes_ida": row["excecoes_ida"] or 0,
            "excecoes_volta": row["excecoes_volta"] or 0,
            "sugestao_frota": {
                "ida": sugerir_frota(total_ida),
                "volta": sugerir_frota(total_volta)
            }
        })

    log.info("Painel consultado: %d dias com reservas", len(resumo))
    return jsonify({"resumo_diario": resumo})


@app.route("/api/checklist/<data>", methods=["GET"])
def api_checklist(data):
    """Lista de passageiros para o motorista (RF05)."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    tipo = request.args.get("tipo", "IDA").upper()
    if tipo not in ("IDA", "VOLTA"):
        return jsonify({"sucesso": False, "erro": "Tipo deve ser IDA ou VOLTA"}), 400

    campo = "ida" if tipo == "IDA" else "volta"

    conn = get_db()
    rows = conn.execute(f"""
        SELECT a.cpf, a.nome, a.tipo_vaga,
               CASE WHEN c.id IS NOT NULL THEN 1 ELSE 0 END as checkin
        FROM reservas r
        JOIN alunos a ON r.cpf = a.cpf
        LEFT JOIN checkins c ON c.cpf = r.cpf AND c.data = r.data AND c.tipo = ?
        WHERE r.data = ? AND r.{campo} = 1 AND r.status = 'ATIVA'
        ORDER BY a.tipo_vaga DESC, a.nome
    """, (tipo, data)).fetchall()
    conn.close()

    passageiros = []
    for row in rows:
        passageiros.append({
            "cpf": row["cpf"],
            "nome": row["nome"],
            "tipo_vaga": row["tipo_vaga"],
            "checkin": bool(row["checkin"])
        })

    log.info("Checklist %s %s: %d passageiros", data, tipo, len(passageiros))
    return jsonify({
        "data": data,
        "tipo": tipo,
        "passageiros": passageiros
    })


@app.route("/api/checkin", methods=["POST"])
def api_checkin():
    """Confirmar embarque fisico (RF05, RS04, RN01, RN02)."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    dados = request.get_json(silent=True) or {}
    cpf = str(dados.get("cpf", "")).strip()
    veiculo_id = str(dados.get("veiculo_id", "")).strip()
    data_str = str(dados.get("data", "")).strip()
    tipo = str(dados.get("tipo", "")).upper()

    if not all([cpf, veiculo_id, data_str, tipo]):
        return jsonify({"sucesso": False, "erro": "Dados incompletos"}), 400

    conn = get_db()

    # Verificar veiculo
    veiculo = conn.execute("SELECT * FROM veiculos WHERE id=? AND ativo=1", (veiculo_id,)).fetchone()
    if not veiculo:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Veiculo nao encontrado"}), 404

    # RS05: Contar vagas de excecao ja blindadas
    excecoes = conn.execute("""
        SELECT COUNT(*) as total FROM reservas r
        JOIN alunos a ON r.cpf = a.cpf
        WHERE r.data=? AND a.tipo_vaga='EXCECAO' AND r.status='ATIVA'
    """, (data_str,)).fetchone()["total"]

    # Contar checkins ja feitos neste veiculo
    checkins_feitos = conn.execute(
        "SELECT COUNT(*) as total FROM checkins WHERE veiculo_id=? AND data=? AND tipo=?",
        (veiculo_id, data_str, tipo)
    ).fetchone()["total"]

    capacidade_total = veiculo["capacidade"]
    vagas_restantes = capacidade_total - checkins_feitos

    if vagas_restantes <= 0:
        conn.close()
        log.info("Checkin REJEITADO: veiculo %s lotado", veiculo_id)
        return jsonify({"sucesso": False, "erro": "Veiculo lotado. Capacidade maxima atingida."}), 409

    # Registrar checkin (ID composto conforme SCHEMA.md)
    checkin_id = f"{cpf}_{veiculo_id}_{data_str}_{tipo}"
    try:
        conn.execute(
            "INSERT INTO checkins (id, cpf, veiculo_id, data, tipo) VALUES (?,?,?,?,?)",
            (checkin_id, cpf, veiculo_id, data_str, tipo)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Checkin ja registrado"}), 409

    vagas_restantes -= 1
    conn.close()

    log.info("Checkin OK: %s no %s (%s) — %d vagas restantes", cpf, veiculo_id, tipo, vagas_restantes)
    return jsonify({
        "sucesso": True,
        "vagas_restantes": vagas_restantes,
        "capacidade_total": capacidade_total
    })


@app.route("/api/veiculos", methods=["GET"])
def api_veiculos():
    """Listar veiculos da frota."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    conn = get_db()
    rows = conn.execute("SELECT * FROM veiculos ORDER BY tipo, id").fetchall()
    conn.close()

    veiculos = []
    for r in rows:
        v = {"id": r["id"], "tipo": r["tipo"], "capacidade": r["capacidade"], "ativo": r["ativo"]}
        try:
            v["nome"] = r["nome"] or ""
        except (IndexError, KeyError):
            v["nome"] = ""
        veiculos.append(v)

    log.info("Frota consultada: %d veiculos", len(veiculos))
    return jsonify(veiculos)


@app.route("/api/veiculos", methods=["POST"])
def api_veiculos_criar():
    """Adicionar novo veiculo a frota."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    dados = request.get_json(silent=True) or {}
    vid = str(dados.get("id", "")).strip().upper()
    nome = str(dados.get("nome", "")).strip()
    tipo = str(dados.get("tipo", "")).strip().upper()
    capacidade = dados.get("capacidade", 0)

    if not vid:
        return jsonify({"sucesso": False, "erro": "ID/Placa obrigatorio"}), 400

    tipos_validos = ["VAN", "MICRO", "ONIBUS", "OUTRO"]
    if tipo not in tipos_validos:
        return jsonify({"sucesso": False, "erro": f"Tipo invalido. Use: {', '.join(tipos_validos)}"}), 400

    try:
        capacidade = int(capacidade)
        if capacidade <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"sucesso": False, "erro": "Capacidade deve ser um numero positivo"}), 400

    conn = get_db()
    # Verificar se ID ja existe
    existente = conn.execute("SELECT id FROM veiculos WHERE id=?", (vid,)).fetchone()
    if existente:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Veiculo com este ID/Placa ja existe"}), 409

    conn.execute(
        "INSERT INTO veiculos (id, nome, tipo, capacidade, ativo) VALUES (?,?,?,?,1)",
        (vid, nome, tipo, capacidade)
    )
    conn.commit()
    conn.close()

    log.info("Veiculo criado: %s (%s, %d lugares)", vid, tipo, capacidade)
    return jsonify({"sucesso": True, "mensagem": "Veiculo adicionado com sucesso."}), 201


@app.route("/api/veiculos/<vid>", methods=["PUT"])
def api_veiculos_editar(vid):
    """Editar veiculo existente."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    dados = request.get_json(silent=True) or {}
    nome = dados.get("nome")
    tipo = dados.get("tipo")
    capacidade = dados.get("capacidade")
    ativo = dados.get("ativo")

    conn = get_db()
    veiculo = conn.execute("SELECT * FROM veiculos WHERE id=?", (vid,)).fetchone()
    if not veiculo:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Veiculo nao encontrado"}), 404

    # Construir UPDATE dinamico
    campos = []
    valores = []

    if nome is not None:
        campos.append("nome=?")
        valores.append(str(nome).strip())

    if tipo is not None:
        tipo_upper = str(tipo).strip().upper()
        tipos_validos = ["VAN", "MICRO", "ONIBUS", "OUTRO"]
        if tipo_upper not in tipos_validos:
            conn.close()
            return jsonify({"sucesso": False, "erro": f"Tipo invalido. Use: {', '.join(tipos_validos)}"}), 400
        campos.append("tipo=?")
        valores.append(tipo_upper)

    if capacidade is not None:
        try:
            cap = int(capacidade)
            if cap <= 0:
                raise ValueError
        except (ValueError, TypeError):
            conn.close()
            return jsonify({"sucesso": False, "erro": "Capacidade deve ser um numero positivo"}), 400
        campos.append("capacidade=?")
        valores.append(cap)

    if ativo is not None:
        campos.append("ativo=?")
        valores.append(1 if ativo else 0)

    if not campos:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Nenhum campo para atualizar"}), 400

    valores.append(vid)
    conn.execute(f"UPDATE veiculos SET {', '.join(campos)} WHERE id=?", valores)
    conn.commit()
    conn.close()

    log.info("Veiculo atualizado: %s", vid)
    return jsonify({"sucesso": True, "mensagem": "Veiculo atualizado com sucesso."})


@app.route("/api/veiculos/<vid>", methods=["DELETE"])
def api_veiculos_excluir(vid):
    """Soft-delete de veiculo (ativo=0)."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    conn = get_db()
    veiculo = conn.execute("SELECT * FROM veiculos WHERE id=?", (vid,)).fetchone()
    if not veiculo:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Veiculo nao encontrado"}), 404

    conn.execute("UPDATE veiculos SET ativo=0 WHERE id=?", (vid,))
    conn.commit()
    conn.close()

    log.info("Veiculo desativado: %s", vid)
    return jsonify({"sucesso": True, "mensagem": "Veiculo removido com sucesso."})


# ══════════════════════════════════════════════
# ROTAS — PASSAGEIROS (CRUD)
# ══════════════════════════════════════════════

@app.route("/api/passageiros", methods=["GET"])
def api_passageiros_listar():
    """Listar passageiros (alunos) cadastrados."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    conn = get_db()
    rows = conn.execute(
        "SELECT cpf, nome, rota, tipo_vaga, ativo FROM alunos ORDER BY nome"
    ).fetchall()
    conn.close()

    passageiros = [{
        "cpf": r["cpf"],
        "nome": r["nome"],
        "rota": r["rota"],
        "tipo_vaga": r["tipo_vaga"],
        "ativo": r["ativo"]
    } for r in rows]

    log.info("Passageiros consultados: %d total", len(passageiros))
    return jsonify(passageiros)


@app.route("/api/passageiros", methods=["POST"])
def api_passageiros_criar():
    """Cadastrar novo passageiro."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    dados = request.get_json(silent=True) or {}
    cpf = str(dados.get("cpf", "")).strip()
    nome = str(dados.get("nome", "")).strip()
    rota = str(dados.get("rota", "")).strip()
    pin = str(dados.get("pin", "")).strip()
    tipo_vaga = str(dados.get("tipo_vaga", "NORMAL")).strip().upper()

    # Validacoes
    if len(cpf) != 11 or not cpf.isdigit():
        return jsonify({"sucesso": False, "erro": "CPF deve conter exatamente 11 digitos numericos"}), 400

    if not nome:
        return jsonify({"sucesso": False, "erro": "Nome obrigatorio"}), 400

    if not rota:
        return jsonify({"sucesso": False, "erro": "Rota obrigatoria"}), 400

    if len(pin) != 4 or not pin.isdigit():
        return jsonify({"sucesso": False, "erro": "PIN deve conter exatamente 4 digitos numericos"}), 400

    if tipo_vaga not in ("NORMAL", "EXCECAO"):
        return jsonify({"sucesso": False, "erro": "Tipo de vaga deve ser NORMAL ou EXCECAO"}), 400

    conn = get_db()
    existente = conn.execute("SELECT cpf, ativo FROM alunos WHERE cpf=?", (cpf,)).fetchone()

    if existente:
        if existente["ativo"] == 0:
            # Reativar aluno desativado com novos dados
            conn.execute(
                "UPDATE alunos SET nome=?, pin=?, rota=?, tipo_vaga=?, ativo=1 WHERE cpf=?",
                (nome, hash_pin(pin), rota, tipo_vaga, cpf)
            )
            conn.commit()
            conn.close()
            log.info("Passageiro reativado: %s (CPF: %s)", nome, cpf)
            return jsonify({"sucesso": True, "mensagem": "Passageiro reativado com sucesso."}), 201
        else:
            conn.close()
            return jsonify({"sucesso": False, "erro": "CPF ja cadastrado e ativo"}), 409

    conn.execute(
        "INSERT INTO alunos (cpf, nome, pin, rota, tipo_vaga, ativo) VALUES (?,?,?,?,?,1)",
        (cpf, nome, hash_pin(pin), rota, tipo_vaga)
    )
    conn.commit()
    conn.close()

    log.info("Passageiro cadastrado: %s (CPF: %s)", nome, cpf)
    return jsonify({"sucesso": True, "mensagem": "Passageiro cadastrado com sucesso."}), 201


@app.route("/api/passageiros/<cpf>", methods=["DELETE"])
def api_passageiros_excluir(cpf):
    """Soft-delete de passageiro (ativo=0)."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    conn = get_db()
    aluno = conn.execute("SELECT * FROM alunos WHERE cpf=?", (cpf,)).fetchone()
    if not aluno:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Passageiro nao encontrado"}), 404

    conn.execute("UPDATE alunos SET ativo=0 WHERE cpf=?", (cpf,))
    conn.commit()
    conn.close()

    log.info("Passageiro desativado: CPF %s", cpf)
    return jsonify({"sucesso": True, "mensagem": "Passageiro removido com sucesso."})


# ══════════════════════════════════════════════
# ROTAS — CONFIGURACOES
# ══════════════════════════════════════════════

@app.route("/api/configuracoes", methods=["GET"])
def api_configuracoes_ler():
    """Ler todas as configuracoes."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    conn = get_db()
    rows = conn.execute("SELECT chave, valor FROM configuracoes").fetchall()
    conn.close()

    config = {r["chave"]: r["valor"] for r in rows}
    return jsonify(config)


@app.route("/api/configuracoes", methods=["PUT"])
def api_configuracoes_atualizar():
    """Atualizar configuracoes (horario_corte, trava_manual)."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    dados = request.get_json(silent=True) or {}

    chaves_permitidas = ["horario_corte", "trava_manual"]
    conn = get_db()

    for chave, valor in dados.items():
        if chave not in chaves_permitidas:
            continue

        # Validacao especifica por chave
        if chave == "horario_corte":
            try:
                partes = str(valor).split(":")
                h = int(partes[0])
                m = int(partes[1]) if len(partes) > 1 else 0
                if not (0 <= h <= 23 and 0 <= m <= 59):
                    raise ValueError
                valor = f"{h:02d}:{m:02d}"
            except (ValueError, IndexError):
                conn.close()
                return jsonify({"sucesso": False, "erro": "Horario invalido. Use formato HH:MM (00:00 a 23:59)"}), 400

        if chave == "trava_manual":
            valor = str(valor).upper()
            if valor not in ("AUTO", "ABERTO", "FECHADO"):
                conn.close()
                return jsonify({"sucesso": False, "erro": "Trava deve ser AUTO, ABERTO ou FECHADO"}), 400

        conn.execute(
            "INSERT INTO configuracoes (chave, valor) VALUES (?,?) ON CONFLICT(chave) DO UPDATE SET valor=?",
            (chave, valor, valor)
        )

    conn.commit()
    conn.close()

    log.info("Configuracoes atualizadas: %s", list(dados.keys()))
    return jsonify({"sucesso": True, "mensagem": "Configuracoes salvas com sucesso."})


@app.route("/api/status-inscricoes", methods=["GET"])
def api_status_inscricoes():
    """Retorna o status atual das inscricoes (aberto/fechado) com motivo."""
    trava = get_config("trava_manual", "AUTO")
    horario = get_config("horario_corte", "14:00")
    agora = get_server_now()

    if trava == "FECHADO":
        status = "FECHADO"
        motivo = "Inscricoes fechadas manualmente pela gestora"
    elif trava == "ABERTO":
        status = "ABERTO"
        motivo = "Inscricoes abertas manualmente pela gestora"
    else:
        # Verificar se o horario de corte ja passou para hoje
        try:
            partes = horario.split(":")
            hora_corte = int(partes[0])
            minuto_corte = int(partes[1]) if len(partes) > 1 else 0
        except (ValueError, IndexError):
            hora_corte = 14
            minuto_corte = 0

        if agora.hour > hora_corte or (agora.hour == hora_corte and agora.minute >= minuto_corte):
            status = "FECHADO"
            motivo = f"Horario de corte atingido ({horario})"
        else:
            status = "ABERTO"
            motivo = f"Inscricoes abertas ate {horario}"

    return jsonify({
        "status": status,
        "motivo": motivo,
        "trava_manual": trava,
        "horario_corte": horario,
        "servidor_utc": datetime.now(timezone.utc).isoformat(),
        "servidor_local": agora.isoformat()
    })


@app.route("/api/server-time", methods=["GET"])
def api_server_time():
    """Retorna a hora atual do servidor em UTC (para validacao anti-burla)."""
    utc_now = datetime.now(timezone.utc)
    local_now = get_server_now()
    return jsonify({
        "utc": utc_now.isoformat(),
        "local": local_now.isoformat(),
        "timezone": SERVER_TIMEZONE,
        "timestamp": int(utc_now.timestamp())
    })


# ══════════════════════════════════════════════
# ROTAS — AVISOS (Requisito A: Mural de Avisos)
# ══════════════════════════════════════════════

@app.route("/api/avisos", methods=["GET"])
def api_avisos_listar():
    """Listar avisos ativos (Publico — WhatsApp-ready). RF06."""
    incluir_expirados = request.args.get("incluir_expirados", "0")

    conn = get_db()

    if incluir_expirados == "1":
        # Requer admin para ver todos (incluindo expirados/arquivados)
        auth_err = require_admin()
        if auth_err:
            conn.close()
            return auth_err
        rows = conn.execute(
            "SELECT * FROM avisos ORDER BY tipo DESC, criado_em DESC"
        ).fetchall()
    else:
        # Publico: so ativos e nao expirados
        rows = conn.execute("""
            SELECT * FROM avisos
            WHERE ativo=1 AND (expira_em IS NULL OR expira_em >= date('now'))
            ORDER BY tipo DESC, criado_em DESC
        """).fetchall()

    conn.close()

    avisos = []
    for r in rows:
        avisos.append({
            "id": r["id"],
            "titulo": r["titulo"],
            "mensagem": r["mensagem"],
            "tipo": r["tipo"],
            "criado_em": r["criado_em"],
            "expira_em": r["expira_em"],
            "ativo": r["ativo"]
        })

    log.info("Avisos consultados: %d", len(avisos))
    return jsonify({"avisos": avisos, "total": len(avisos)})


@app.route("/api/avisos", methods=["POST"])
def api_avisos_criar():
    """Criar novo aviso (Admin). RF06."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    dados = request.get_json(silent=True) or {}
    titulo = str(dados.get("titulo", "")).strip()
    mensagem = str(dados.get("mensagem", "")).strip()
    tipo = str(dados.get("tipo", "INFO")).strip().upper()
    expira_em = dados.get("expira_em")

    # Validacoes
    if not titulo or len(titulo) > 100:
        return jsonify({"sucesso": False, "erro": "Titulo obrigatorio (max 100 caracteres)"}), 400
    if not mensagem or len(mensagem) > 500:
        return jsonify({"sucesso": False, "erro": "Mensagem obrigatoria (max 500 caracteres)"}), 400
    if tipo not in ("URGENTE", "INFO"):
        return jsonify({"sucesso": False, "erro": "Tipo deve ser URGENTE ou INFO"}), 400

    if expira_em:
        try:
            exp_date = date.fromisoformat(str(expira_em))
        except ValueError:
            return jsonify({"sucesso": False, "erro": "Data de expiracao invalida (YYYY-MM-DD)"}), 400
    else:
        expira_em = None

    # Verificar limite de avisos ativos
    conn = get_db()
    limite = int(get_config("limite_avisos", "10"))
    ativos = conn.execute(
        "SELECT COUNT(*) as total FROM avisos WHERE ativo=1 AND (expira_em IS NULL OR expira_em >= date('now'))"
    ).fetchone()["total"]

    if ativos >= limite:
        conn.close()
        return jsonify({"sucesso": False, "erro": f"Limite de {limite} avisos ativos atingido. Arquive avisos antigos."}), 409

    aviso_id = f"AV-{int(time.time() * 1000)}"
    conn.execute(
        "INSERT INTO avisos (id, titulo, mensagem, tipo, expira_em) VALUES (?,?,?,?,?)",
        (aviso_id, titulo, mensagem, tipo, expira_em)
    )
    conn.commit()
    conn.close()

    log.info("Aviso criado: %s (%s) — %s", aviso_id, tipo, titulo)
    return jsonify({"sucesso": True, "mensagem": "Aviso publicado com sucesso.", "id": aviso_id}), 201


@app.route("/api/avisos/<aviso_id>", methods=["PUT"])
def api_avisos_editar(aviso_id):
    """Editar aviso existente (Admin). RF06."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    dados = request.get_json(silent=True) or {}
    conn = get_db()

    aviso = conn.execute("SELECT * FROM avisos WHERE id=?", (aviso_id,)).fetchone()
    if not aviso:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Aviso nao encontrado"}), 404

    campos = []
    valores = []

    titulo = dados.get("titulo")
    if titulo is not None:
        titulo = str(titulo).strip()
        if not titulo or len(titulo) > 100:
            conn.close()
            return jsonify({"sucesso": False, "erro": "Titulo obrigatorio (max 100 caracteres)"}), 400
        campos.append("titulo=?")
        valores.append(titulo)

    mensagem = dados.get("mensagem")
    if mensagem is not None:
        mensagem = str(mensagem).strip()
        if not mensagem or len(mensagem) > 500:
            conn.close()
            return jsonify({"sucesso": False, "erro": "Mensagem obrigatoria (max 500 caracteres)"}), 400
        campos.append("mensagem=?")
        valores.append(mensagem)

    tipo = dados.get("tipo")
    if tipo is not None:
        tipo = str(tipo).strip().upper()
        if tipo not in ("URGENTE", "INFO"):
            conn.close()
            return jsonify({"sucesso": False, "erro": "Tipo deve ser URGENTE ou INFO"}), 400
        campos.append("tipo=?")
        valores.append(tipo)

    if "expira_em" in dados:
        expira_em = dados["expira_em"]
        if expira_em:
            try:
                date.fromisoformat(str(expira_em))
            except ValueError:
                conn.close()
                return jsonify({"sucesso": False, "erro": "Data de expiracao invalida (YYYY-MM-DD)"}), 400
        else:
            expira_em = None
        campos.append("expira_em=?")
        valores.append(expira_em)

    if not campos:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Nenhum campo para atualizar"}), 400

    valores.append(aviso_id)
    conn.execute(f"UPDATE avisos SET {', '.join(campos)} WHERE id=?", valores)
    conn.commit()
    conn.close()

    log.info("Aviso atualizado: %s", aviso_id)
    return jsonify({"sucesso": True, "mensagem": "Aviso atualizado com sucesso."})


@app.route("/api/avisos/<aviso_id>", methods=["DELETE"])
def api_avisos_arquivar(aviso_id):
    """Arquivar aviso (soft-delete: ativo=0). Admin."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    conn = get_db()
    aviso = conn.execute("SELECT * FROM avisos WHERE id=?", (aviso_id,)).fetchone()
    if not aviso:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Aviso nao encontrado"}), 404

    conn.execute("UPDATE avisos SET ativo=0 WHERE id=?", (aviso_id,))
    conn.commit()
    conn.close()

    log.info("Aviso arquivado: %s", aviso_id)
    return jsonify({"sucesso": True, "mensagem": "Aviso arquivado com sucesso."})


# ══════════════════════════════════════════════
# ROTAS — GESTÃO DE ROTAS
# ══════════════════════════════════════════════

@app.route("/api/rotas", methods=["GET"])
def api_rotas_listar():
    """Listar rotas. Admin."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    conn = get_db()
    rows = conn.execute("SELECT * FROM rotas ORDER BY nome").fetchall()
    conn.close()

    rotas = [{"id": r["id"], "nome": r["nome"], "ativo": r["ativo"]} for r in rows]
    return jsonify({"rotas": rotas})

@app.route("/api/rotas", methods=["POST"])
def api_rotas_criar():
    """Criar nova rota. Admin."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    dados = request.get_json(silent=True) or {}
    nome = str(dados.get("nome", "")).strip()

    if not nome:
        return jsonify({"sucesso": False, "erro": "Nome da rota obrigatorio"}), 400

    import unicodedata
    import re
    # Gerar slug do nome
    slug = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
    slug = re.sub(r'[^a-zA-Z0-9]', '', slug).upper()
    rota_id = f"ROTA-{slug[:15]}"

    conn = get_db()
    existente = conn.execute("SELECT id FROM rotas WHERE id=?", (rota_id,)).fetchone()
    if existente:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Uma rota similar ja existe"}), 409

    conn.execute("INSERT INTO rotas (id, nome) VALUES (?,?)", (rota_id, nome))
    conn.commit()
    conn.close()

    log.info("Rota criada: %s (%s)", rota_id, nome)
    return jsonify({"sucesso": True, "mensagem": "Rota criada com sucesso.", "id": rota_id}), 201

@app.route("/api/rotas/<rota_id>", methods=["DELETE"])
def api_rotas_excluir(rota_id):
    """Excluir rota. Admin."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    conn = get_db()
    # Verifica se existem pontos atrelados
    pontos = conn.execute("SELECT count(*) as total FROM pontos_rota WHERE rota_id=?", (rota_id,)).fetchone()["total"]
    if pontos > 0:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Nao e possivel excluir. Existem pontos associados a esta rota."}), 409

    conn.execute("DELETE FROM rotas WHERE id=?", (rota_id,))
    conn.commit()
    conn.close()

    return jsonify({"sucesso": True, "mensagem": "Rota removida com sucesso."})


# ══════════════════════════════════════════════
# ROTAS — PONTOS DE ROTA (Requisito B)
# ══════════════════════════════════════════════

@app.route("/api/pontos-rota", methods=["GET"])
def api_pontos_rota_listar():
    """Listar pontos de rota. RF07."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    rota_filtro = request.args.get("rota", "").strip()
    conn = get_db()

    if rota_filtro:
        rows = conn.execute("""
            SELECT p.*, r.nome as rota_nome 
            FROM pontos_rota p 
            JOIN rotas r ON p.rota_id = r.id 
            WHERE p.rota_id=? ORDER BY p.ordem
        """, (rota_filtro,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT p.*, r.nome as rota_nome 
            FROM pontos_rota p 
            JOIN rotas r ON p.rota_id = r.id 
            ORDER BY r.nome, p.ordem
        """).fetchall()
    conn.close()

    pontos = [{"id": r["id"], "rota_id": r["rota_id"], "rota_nome": r["rota_nome"], "nome": r["nome"], "ordem": r["ordem"]} for r in rows]
    log.info("Pontos de rota consultados: %d", len(pontos))
    return jsonify({"pontos": pontos})


@app.route("/api/pontos-rota", methods=["POST"])
def api_pontos_rota_criar():
    """Cadastrar ponto de rota. Admin."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    dados = request.get_json(silent=True) or {}
    rota_id = str(dados.get("rota_id", "")).strip()
    nome = str(dados.get("nome", "")).strip()
    ordem = dados.get("ordem", 0)

    if not rota_id:
        return jsonify({"sucesso": False, "erro": "Rota obrigatoria"}), 400
    if not nome:
        return jsonify({"sucesso": False, "erro": "Nome do ponto obrigatorio"}), 400

    try:
        ordem = int(ordem)
        if ordem <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"sucesso": False, "erro": "Ordem deve ser um numero positivo"}), 400

    conn = get_db()
    # Verifica se a rota existe
    rota = conn.execute("SELECT id FROM rotas WHERE id=?", (rota_id,)).fetchone()
    if not rota:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Rota invalida"}), 400

    # Gerar ID
    slug = rota_id.replace("ROTA-", "").upper()[:15]
    ponto_id = f"PR-{slug}-{ordem}"

    existente = conn.execute("SELECT id FROM pontos_rota WHERE id=?", (ponto_id,)).fetchone()
    if existente:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Ponto com este ID ja existe. Altere a ordem."}), 409

    conn.execute(
        "INSERT INTO pontos_rota (id, rota_id, nome, ordem) VALUES (?,?,?,?)",
        (ponto_id, rota_id, nome, ordem)
    )
    conn.commit()
    conn.close()

    log.info("Ponto de rota criado: %s (%s #%d)", ponto_id, nome, ordem)
    return jsonify({"sucesso": True, "mensagem": "Ponto cadastrado com sucesso.", "id": ponto_id}), 201

@app.route("/api/pontos-rota/<ponto_id>", methods=["PUT"])
def api_pontos_rota_editar(ponto_id):
    """Editar ponto de rota existente. Admin."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    dados = request.get_json(silent=True) or {}
    nome = dados.get("nome")
    ordem = dados.get("ordem")

    conn = get_db()
    ponto = conn.execute("SELECT * FROM pontos_rota WHERE id=?", (ponto_id,)).fetchone()
    if not ponto:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Ponto nao encontrado"}), 404

    campos = []
    valores = []

    if nome is not None:
        nome = str(nome).strip()
        if not nome:
            conn.close()
            return jsonify({"sucesso": False, "erro": "Nome do ponto obrigatorio"}), 400
        campos.append("nome=?")
        valores.append(nome)

    if ordem is not None:
        try:
            ordem = int(ordem)
            if ordem <= 0:
                raise ValueError
        except (ValueError, TypeError):
            conn.close()
            return jsonify({"sucesso": False, "erro": "Ordem deve ser um numero positivo"}), 400
        campos.append("ordem=?")
        valores.append(ordem)

    if not campos:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Nenhum campo para atualizar"}), 400

    valores.append(ponto_id)
    conn.execute(f"UPDATE pontos_rota SET {', '.join(campos)} WHERE id=?", valores)
    conn.commit()
    conn.close()

    log.info("Ponto de rota atualizado: %s", ponto_id)
    return jsonify({"sucesso": True, "mensagem": "Ponto atualizado com sucesso."})

@app.route("/api/pontos-rota/<ponto_id>", methods=["DELETE"])
def api_pontos_rota_excluir(ponto_id):
    """Remover ponto de rota. Admin."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    conn = get_db()
    ponto = conn.execute("SELECT * FROM pontos_rota WHERE id=?", (ponto_id,)).fetchone()
    if not ponto:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Ponto nao encontrado"}), 404

    conn.execute("DELETE FROM pontos_rota WHERE id=?", (ponto_id,))
    conn.commit()
    conn.close()

    log.info("Ponto de rota removido: %s", ponto_id)
    return jsonify({"sucesso": True, "mensagem": "Ponto removido com sucesso."})


# ══════════════════════════════════════════════
# ROTAS — STATUS DE VIAGEM (Requisito B)
# ══════════════════════════════════════════════

@app.route("/api/status-viagem", methods=["PUT"])
def api_status_viagem_atualizar():
    """Motorista atualiza posicao do veiculo. RS07."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    dados = request.get_json(silent=True) or {}
    veiculo_id = str(dados.get("veiculo_id", "")).strip()
    data_str = str(dados.get("data", "")).strip()
    tipo = str(dados.get("tipo", "")).upper()
    ponto_id = str(dados.get("ponto_id", "")).strip()

    if not all([veiculo_id, data_str, tipo, ponto_id]):
        return jsonify({"sucesso": False, "erro": "Dados incompletos"}), 400
    if tipo not in ("IDA", "VOLTA"):
        return jsonify({"sucesso": False, "erro": "Tipo deve ser IDA ou VOLTA"}), 400

    conn = get_db()

    # Verificar ponto de rota existe
    ponto = conn.execute("SELECT * FROM pontos_rota WHERE id=?", (ponto_id,)).fetchone()
    if not ponto:
        conn.close()
        return jsonify({"sucesso": False, "erro": "Ponto de rota nao encontrado"}), 404

    # Verificar se e o ultimo ponto da rota
    ultimo_ponto = conn.execute(
        "SELECT MAX(ordem) as max_ordem FROM pontos_rota WHERE rota_id=?", (ponto["rota_id"],)
    ).fetchone()
    is_ultimo = (ponto["ordem"] == ultimo_ponto["max_ordem"]) if ultimo_ponto else False
    novo_status = "FINALIZADA" if is_ultimo else "EM_ROTA"

    # Proximo ponto
    proximo = conn.execute(
        "SELECT nome FROM pontos_rota WHERE rota_id=? AND ordem>? ORDER BY ordem LIMIT 1",
        (ponto["rota_id"], ponto["ordem"])
    ).fetchone()
    proximo_ponto = proximo["nome"] if proximo else None

    # UPSERT status_viagem
    viagem_id = f"{veiculo_id}_{data_str}_{tipo}"
    agora = get_server_now().isoformat()

    conn.execute("""
        INSERT INTO status_viagem (id, veiculo_id, data, tipo, ponto_atual_id, status, atualizado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET ponto_atual_id=?, status=?, atualizado_em=?
    """, (viagem_id, veiculo_id, data_str, tipo, ponto_id, novo_status, agora,
          ponto_id, novo_status, agora))
    conn.commit()
    conn.close()

    log.info("Status viagem: %s -> %s (%s) em %s", veiculo_id, ponto["nome"], novo_status, data_str)
    return jsonify({
        "sucesso": True,
        "status": novo_status,
        "ponto_atual": ponto["nome"],
        "proximo_ponto": proximo_ponto,
        "atualizado_em": agora
    })


@app.route("/api/status-viagem/<data>", methods=["GET"])
def api_status_viagem_consultar(data):
    """Consultar status de viagens do dia (Publico — WhatsApp-ready). RF07."""
    tipo_filtro = request.args.get("tipo", "").upper()

    conn = get_db()

    if tipo_filtro and tipo_filtro in ("IDA", "VOLTA"):
        rows = conn.execute(
            "SELECT * FROM status_viagem WHERE data=? AND tipo=?", (data, tipo_filtro)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM status_viagem WHERE data=?", (data,)
        ).fetchall()

    viagens = []
    for r in rows:
        ponto_atual_nome = None
        ponto_ordem_atual = 0
        total_pontos = 0
        proximo_ponto = None
        rota_nome = None
        rota_id = None

        if r["ponto_atual_id"]:
            ponto = conn.execute("""
                SELECT p.*, rt.nome as rnome 
                FROM pontos_rota p 
                LEFT JOIN rotas rt ON p.rota_id = rt.id 
                WHERE p.id=?
            """, (r["ponto_atual_id"],)).fetchone()
            
            if ponto:
                ponto_atual_nome = ponto["nome"]
                ponto_ordem_atual = ponto["ordem"]
                rota_nome = ponto["rnome"]
                rota_id = ponto["rota_id"]
                # Total de pontos da mesma rota
                total = conn.execute(
                    "SELECT COUNT(*) as cnt FROM pontos_rota WHERE rota_id=?", (ponto["rota_id"],)
                ).fetchone()
                total_pontos = total["cnt"] if total else 0
                # Proximo ponto
                proximo = conn.execute(
                    "SELECT nome FROM pontos_rota WHERE rota_id=? AND ordem>? ORDER BY ordem LIMIT 1",
                    (ponto["rota_id"], ponto["ordem"])
                ).fetchone()
                proximo_ponto = proximo["nome"] if proximo else None

        viagens.append({
            "veiculo_id": r["veiculo_id"],
            "tipo": r["tipo"],
            "status": r["status"],
            "ponto_atual": ponto_atual_nome,
            "ponto_ordem_atual": ponto_ordem_atual,
            "total_pontos": total_pontos,
            "proximo_ponto": proximo_ponto,
            "atualizado_em": r["atualizado_em"],
            "rota_nome": rota_nome,
            "rota_id": rota_id
        })

    conn.close()
    log.info("Status viagem consultado para %s: %d viagens", data, len(viagens))
    return jsonify({"viagens": viagens})

# ══════════════════════════════════════════════
# ROTAS — RELATÓRIOS
# ══════════════════════════════════════════════

import io
import csv
from flask import Response

@app.route("/api/relatorios/viagens", methods=["GET"])
def api_relatorio_viagens():
    """Gera CSV de viagens consolidadas. Admin."""
    auth_err = require_admin()
    if auth_err:
        return auth_err

    data_inicio = request.args.get("data_inicio", "")
    data_fim = request.args.get("data_fim", "")

    if not data_inicio or not data_fim:
        return jsonify({"sucesso": False, "erro": "data_inicio e data_fim obrigatorios"}), 400

    conn = get_db()
    # Consulta: dados de checkins + alunos
    query = """
        SELECT c.data, c.tipo, c.veiculo_id, a.cpf, a.nome, a.rota, c.confirmado_em
        FROM checkins c
        JOIN alunos a ON c.cpf = a.cpf
        WHERE c.data >= ? AND c.data <= ?
        ORDER BY c.data, c.tipo, c.veiculo_id, c.confirmado_em
    """
    rows = conn.execute(query, (data_inicio, data_fim)).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['Data', 'Tipo', 'Veiculo', 'CPF Aluno', 'Nome Aluno', 'Rota do Aluno', 'Horario Checkin'])

    for row in rows:
        writer.writerow([
            row["data"], 
            row["tipo"], 
            row["veiculo_id"], 
            row["cpf"], 
            row["nome"], 
            row["rota"], 
            row["confirmado_em"]
        ])

    csv_data = output.getvalue()
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=relatorio_viagens_{data_inicio}_a_{data_fim}.csv"}
    )


# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════

if __name__ == "__main__":
    init_db()
    log.info("=" * 50)
    log.info("  VEM SPTU — Motor Backend")
    log.info("  http://127.0.0.1:5000")
    log.info("  Admin Token: %s", ADMIN_TOKEN)
    log.info("=" * 50)
    app.run(host="127.0.0.1", port=5000, debug=True)
