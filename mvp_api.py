#!/usr/bin/env python3
"""Cliente de linha de comando da API do MVP Experts (só biblioteca padrão).

Configuração: variáveis MVP_API_URL e MVP_API_TOKEN (prioridade) ou
~/.config/mvp-experts/<instancia>.env (padrão: api.env). O token nunca é impresso.
"""
import argparse
import datetime
import json
import os
import socket
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

CONFIG_DIR = os.path.expanduser("~/.config/mvp-experts")


class ApiError(Exception):
    pass


def sair_sem_config(msg):
    sys.stderr.write(
        f"Configuração ausente: {msg}\n"
        "Crie ~/.config/mvp-experts/<instancia>.env (pasta 700, arquivo 600) com:\n"
        "    MVP_API_URL=https://mvpexperts.conexaogtecnologia.com.br/api\n"
        "    MVP_API_TOKEN=<token>\n"
        "ou exporte MVP_API_URL e MVP_API_TOKEN.\n"
        "Para gerar o token: no MVP Experts, Integrações > Gerar Nova Chave API "
        "(exige a permissão \"gerir integrações\").\n"
    )
    sys.exit(2)


def carregar_config(instancia):
    arquivo = os.path.join(CONFIG_DIR, f"{instancia}.env")
    valores = {}
    if os.path.isfile(arquivo):
        try:
            with open(arquivo, encoding="utf-8") as f:
                for linha in f:
                    linha = linha.strip()
                    if not linha or linha.startswith("#") or "=" not in linha:
                        continue
                    chave, valor = linha.split("=", 1)
                    if chave.strip().startswith("export "):
                        chave = chave.strip()[7:]
                    valores[chave.strip()] = valor.strip().strip('"').strip("'")
        except OSError as e:
            sair_sem_config(f"não foi possível ler {arquivo} ({e.strerror})")
    maquina = os.environ.get("MVP_MAQUINA") or valores.get("MVP_MAQUINA") or socket.gethostname()
    url = os.environ.get("MVP_API_URL") or valores.get("MVP_API_URL")
    token = os.environ.get("MVP_API_TOKEN") or valores.get("MVP_API_TOKEN")
    if not url or not token:
        faltando = ", ".join(n for n, v in (("MVP_API_URL", url), ("MVP_API_TOKEN", token)) if not v)
        sair_sem_config(f"{faltando} não definido (instância '{instancia}', arquivo {arquivo})")
    return url.rstrip("/"), token, maquina


class Cliente:
    def __init__(self, url, token, maquina=None):
        self.url = url
        self.token = token
        self.maquina = maquina
        self.ctx = None
        if os.environ.get("MVP_API_INSECURE") == "1":
            self.ctx = ssl._create_unverified_context()

    @property
    def base_web(self):
        return self.url[:-4] if self.url.endswith("/api") else self.url

    def req(self, metodo, caminho, corpo=None, query=None):
        url = self.url + caminho
        if query:
            q = {k: v for k, v in query.items() if v is not None}
            if q:
                url += "?" + urllib.parse.urlencode(q, doseq=True)
        dados = None
        headers = {"Accept": "application/json", "Authorization": f"Bearer {self.token}"}
        if corpo is not None:
            dados = json.dumps({k: v for k, v in corpo.items() if v is not None}).encode()
            headers["Content-Type"] = "application/json"
        r = urllib.request.Request(url, data=dados, method=metodo, headers=headers)
        try:
            with urllib.request.urlopen(r, context=self.ctx, timeout=30) as resp:
                bruto = resp.read().decode("utf-8")
                return json.loads(bruto) if bruto.strip() else None
        except urllib.error.HTTPError as e:
            raise ApiError(self._mensagem_erro(e)) from None
        except urllib.error.URLError as e:
            raise ApiError(f"Falha de conexão com {self.url}: {e.reason}") from None

    @staticmethod
    def _mensagem_erro(e):
        try:
            corpo = json.loads(e.read().decode("utf-8"))
        except Exception:
            corpo = {}
        padrao = {
            401: "Token inválido ou revogado (401).",
            403: "Sem permissão (403). Verifique se você participa do projeto (convite pendente?).",
            404: "Não encontrado (404).",
            429: "Limite de requisições atingido (429). Aguarde e tente de novo.",
        }
        msg = corpo.get("message") if isinstance(corpo, dict) else None
        partes = [f"HTTP {e.code}: {msg or padrao.get(e.code, e.reason)}"]
        erros = corpo.get("errors") if isinstance(corpo, dict) else None
        if isinstance(erros, dict):
            for campo, lista in erros.items():
                for m in lista if isinstance(lista, list) else [lista]:
                    partes.append(f"  - {campo}: {m}")
        return "\n".join(partes)


def dados(resp):
    return resp.get("data") if isinstance(resp, dict) and "data" in resp else resp


def com_url(resp, url):
    d = dados(resp)
    if isinstance(d, dict):
        d = dict(d, url=url)
    return {"data": d}


def com_maquina(descricao, c):
    """Marca o lançamento com a máquina de origem, para saber onde o trabalho foi feito."""
    if not c.maquina:
        return descricao
    marca = f"[{c.maquina}]"
    if descricao and marca in descricao:
        return descricao
    return f"{descricao} {marca}" if descricao else marca


def todos_projetos(c):
    projetos, pagina = [], 1
    while True:
        r = c.req("GET", "/projects", query={"per_page": 100, "page": pagina})
        projetos += r.get("data", [])
        meta = r.get("meta") or {}
        if pagina >= meta.get("last_page", 1):
            return projetos
        pagina += 1


def normalizar_data_hora(valor):
    """Aceita 'AAAA-MM-DD HH:MM' ou ISO 8601 (com Z/deslocamento); repassa ao servidor."""
    return valor.strip() if valor else valor


def executar(args, c):
    cmd = args.cmd
    if cmd == "eu":
        return c.req("GET", "/auth/me")
    if cmd == "projetos":
        return c.req("GET", "/projects", query={
            "q": args.q, "mine": 1 if args.meus else None,
            "status": args.status, "per_page": args.por_pagina})
    if cmd == "projeto-criar":
        r = c.req("POST", "/projects", {
            "title": args.titulo, "description": args.descricao, "objective": args.objetivo,
            "institutions": args.instituicao, "type": args.tipo,
            "start_date": args.inicio, "end_date": args.fim})
        return com_url(r, f"{c.base_web}/projetos/{dados(r)['id']}")
    if cmd == "tarefas":
        return c.req("GET", f"/projects/{args.projeto}/tasks", query={
            "q": args.q, "status": args.status, "per_page": args.por_pagina})
    if cmd == "tarefa-criar":
        responsaveis = list(args.responsavel or [])
        if args.eu:
            me = dados(c.req("GET", "/auth/me"))
            if me["id"] not in responsaveis:
                responsaveis.append(me["id"])
        r = c.req("POST", f"/projects/{args.projeto}/tasks", {
            "title": args.titulo, "priority": args.prioridade, "description": args.descricao,
            "start_date": args.inicio, "due_date": args.prazo,
            "hours_estimated": args.horas_estimadas,
            "assignees": responsaveis or None})
        return com_url(r, f"{c.base_web}/tarefas/{dados(r)['id']}")
    if cmd == "tarefa-status":
        return c.req("PATCH", f"/tasks/{args.tarefa}/status", {"status": args.status})
    if cmd == "iniciar":
        return c.req("POST", "/timesheet/start", {
            "project_id": args.projeto, "task_id": args.tarefa,
            "description": com_maquina(args.descricao, c)})
    if cmd == "parar":
        return c.req("POST", "/timesheet/stop", {})
    if cmd == "rodando":
        r = c.req("GET", "/timesheet/running")
        return r if r is not None else {"data": None}
    if cmd == "horas":
        return c.req("POST", "/timesheet/entries", {
            "project_id": args.projeto, "task_id": args.tarefa,
            "description": com_maquina(args.descricao, c),
            "started_at": normalizar_data_hora(args.inicio),
            "ended_at": normalizar_data_hora(args.fim), "duration_minutes": args.minutos})
    if cmd == "resumo":
        return c.req("GET", f"/projects/{args.projeto}/timesheet/summary",
                     query={"from": args.de, "to": args.ate})
    if cmd == "dia":
        data = args.data or datetime.date.today().isoformat()
        me = dados(c.req("GET", "/auth/me"))
        linhas, total = [], 0.0
        for p in todos_projetos(c):
            if p.get("status") == "cancelled":
                continue
            s = dados(c.req("GET", f"/projects/{p['id']}/timesheet/summary",
                            query={"from": data, "to": data}))
            meu = sum(u.get("hours", 0) for u in s.get("by_user", []) if u.get("user_id") == me["id"])
            if meu:
                total += meu
                linhas.append({"projeto_id": p["id"], "projeto": p["title"], "horas": meu,
                               "tarefas": s.get("by_task", [])})
        return {"data": {"dia": data, "usuario": me["name"], "maquina_atual": c.maquina,
                         "total_horas": round(total, 2), "projetos": linhas}}
    raise ApiError(f"Comando desconhecido: {cmd}")


def montar_parser():
    p = argparse.ArgumentParser(prog="mvp_api.py", description="Cliente da API do MVP Experts.")
    p.add_argument("--instancia", default="api",
                   help="arquivo ~/.config/mvp-experts/<instancia>.env (padrão: api)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("eu", help="usuário dono do token")

    s = sub.add_parser("projetos", help="listar/procurar projetos")
    s.add_argument("--q")
    s.add_argument("--meus", action="store_true")
    s.add_argument("--status")
    s.add_argument("--por-pagina", type=int)

    s = sub.add_parser("projeto-criar", help="criar projeto")
    s.add_argument("--titulo", required=True)
    s.add_argument("--descricao", required=True)
    s.add_argument("--objetivo", required=True)
    s.add_argument("--instituicao", type=int, action="append", required=True)
    s.add_argument("--tipo")
    s.add_argument("--inicio", help="AAAA-MM-DD")
    s.add_argument("--fim", help="AAAA-MM-DD")

    s = sub.add_parser("tarefas", help="listar tarefas do projeto")
    s.add_argument("projeto", type=int)
    s.add_argument("--q")
    s.add_argument("--status", choices=["todo", "doing", "done", "cancelled"])
    s.add_argument("--por-pagina", type=int)

    s = sub.add_parser("tarefa-criar", help="criar tarefa")
    s.add_argument("projeto", type=int)
    s.add_argument("--titulo", required=True)
    s.add_argument("--prioridade", default="medium", choices=["low", "medium", "high", "critical"])
    s.add_argument("--descricao")
    s.add_argument("--inicio", help="AAAA-MM-DD")
    s.add_argument("--prazo", help="AAAA-MM-DD")
    s.add_argument("--horas-estimadas", type=float)
    s.add_argument("--responsavel", type=int, action="append")
    s.add_argument("--eu", action="store_true", help="atribuir a mim")

    s = sub.add_parser("tarefa-status", help="mudar estado da tarefa")
    s.add_argument("tarefa", type=int)
    s.add_argument("--status", required=True, choices=["todo", "doing", "done", "cancelled"])

    s = sub.add_parser("iniciar", help="ligar cronômetro")
    s.add_argument("projeto", type=int)
    s.add_argument("--tarefa", type=int)
    s.add_argument("--descricao")

    sub.add_parser("parar", help="parar cronômetro")
    sub.add_parser("rodando", help="cronômetro atual")

    s = sub.add_parser("horas", help="lançar horas")
    s.add_argument("projeto", type=int)
    s.add_argument("--inicio", required=True, help='"AAAA-MM-DD HH:MM" ou ISO 8601')
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--fim")
    g.add_argument("--minutos", type=int)
    s.add_argument("--tarefa", type=int)
    s.add_argument("--descricao")

    s = sub.add_parser("dia", help="minhas horas lançadas num dia, em todos os projetos")
    s.add_argument("data", nargs="?", help="AAAA-MM-DD (padrão: hoje)")

    s = sub.add_parser("resumo", help="resumo de horas do projeto")
    s.add_argument("projeto", type=int)
    s.add_argument("--de", help="AAAA-MM-DD")
    s.add_argument("--ate", help="AAAA-MM-DD")
    return p


def main():
    args = montar_parser().parse_args()
    if args.cmd == "horas" and args.minutos is not None and not 1 <= args.minutos <= 1440:
        sys.stderr.write("--minutos deve estar entre 1 e 1440.\n")
        sys.exit(1)
    url, token, maquina = carregar_config(args.instancia)
    try:
        resultado = executar(args, Cliente(url, token, maquina))
    except ApiError as e:
        sys.stderr.write(str(e) + "\n")
        sys.exit(1)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
