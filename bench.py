"""Decisão tipada (Clef) vs LLM generativo com JSON mode, no Workers AI.

Mesmas 3 perguntas sobre os mesmos tickets rotulados.
Uso: python bench.py @cf/cloudflare/clef [--repeticoes 3]
     python bench.py @cf/meta/llama-3.3-70b-instruct-fp8-fast
Lê CLOUDFLARE_ACCOUNT_ID e CLOUDFLARE_API_TOKEN do ambiente.
"""
import argparse
import json
import os
import statistics
import time
import urllib.error
import urllib.request

from tickets import DEPARTAMENTOS, TICKETS

BASE = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}/ai/run/"
TOKEN = os.environ["CLOUDFLARE_API_TOKEN"]

INSTRUCAO_DEPTO = "Qual departamento deve receber este ticket?"
INSTRUCAO_URGENTE = "O ticket é urgente?"
INSTRUCAO_FRUSTRACAO = "Quão frustrado está o cliente?"
NIVEIS = ["calmo", "incomodado", "irritado"]
MODO_OBJETO = False


def post(modelo: str, corpo: dict) -> dict:
    req = urllib.request.Request(
        BASE + modelo,
        data=json.dumps(corpo).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.load(resp)["result"]
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}") from e


def decidir_clef(modelo: str, ticket: str) -> tuple[dict, dict]:
    corpo = {
        "model": modelo.rsplit("/", 1)[-1],
        "state": ticket,
        "questions": {
            "departamento": {"type": "choice", "instructions": INSTRUCAO_DEPTO,
                             "criteria": DEPARTAMENTOS},
            "urgente": {"type": "noul", "instructions": INSTRUCAO_URGENTE},
            "frustracao": {"type": "score", "instructions": INSTRUCAO_FRUSTRACAO,
                           "criteria": NIVEIS},
        },
    }
    r = post(modelo, corpo)
    a = r["answers"]
    decisao = {
        "departamento": a["departamento"]["choice"],
        "urgente": a["urgente"]["noul"] >= 0.5,
        "frustracao": NIVEIS[round(a["frustracao"]["score"])],
    }
    return decisao, r["usage"]


SCHEMA = {
    "type": "object",
    "properties": {
        "departamento": {"type": "string", "enum": list(DEPARTAMENTOS)},
        "urgente": {"type": "boolean"},
        "frustracao": {"type": "string", "enum": NIVEIS},
    },
    "required": ["departamento", "urgente", "frustracao"],
    "additionalProperties": False,
}


def decidir_generativo(modelo: str, ticket: str) -> tuple[dict, dict]:
    criterios = "; ".join(f"{k}: {v}" for k, v in DEPARTAMENTOS.items())
    corpo = {
        "messages": [
            {"role": "system", "content": "Você classifica tickets de suporte. Responda só com JSON."},
            {"role": "user", "content": (
                f"Ticket: {ticket}\n\n1. {INSTRUCAO_DEPTO} Opções: {criterios}\n"
                f"2. {INSTRUCAO_URGENTE} (true/false)\n"
                f"3. {INSTRUCAO_FRUSTRACAO} Opções: {', '.join(NIVEIS)}"
                + ("\n\nResponda com um objeto JSON com as chaves "
                   '"departamento", "urgente" (boolean) e "frustracao".' if MODO_OBJETO else "")
            )},
        ],
        "response_format": ({"type": "json_object"} if MODO_OBJETO
                            else {"type": "json_schema", "json_schema": SCHEMA}),
        "max_tokens": 200,
        "temperature": 0,
    }
    r = post(modelo, corpo)
    bruto = r.get("response")
    if bruto is None and "choices" in r:
        bruto = r["choices"][0]["message"]["content"]
    decisao = bruto if isinstance(bruto, dict) else json.loads(bruto)
    # Valida o contrato: o que o schema prometia, o código confere
    if (decisao["departamento"] not in DEPARTAMENTOS
            or not isinstance(decisao["urgente"], bool)
            or decisao["frustracao"] not in NIVEIS):
        raise ValueError(f"fora do contrato: {decisao}")
    return decisao, r.get("usage", {})


def p(valores: list[float], q: float) -> float:
    ordenados = sorted(valores)
    return ordenados[min(len(ordenados) - 1, int(q * len(ordenados)))]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("modelo")
    ap.add_argument("--repeticoes", type=int, default=3)
    ap.add_argument("--json-object", action="store_true",
                    help="para modelos sem suporte a json_schema: JSON livre, contrato só no prompt")
    args = ap.parse_args()
    global MODO_OBJETO
    MODO_OBJETO = args.json_object
    decidir = decidir_clef if "/clef" in args.modelo else decidir_generativo

    latencias, erros, erros_http, acertos_depto, acertos_urg, total = [], [], [], 0, 0, 0
    tokens_in = tokens_out = 0
    for t in TICKETS:
        for _ in range(args.repeticoes):
            t0 = time.perf_counter()
            try:
                decisao, uso = decidir(args.modelo, t["texto"])
            except RuntimeError as e:
                erros_http.append(str(e))
                continue
            except (ValueError, KeyError, json.JSONDecodeError) as e:
                erros.append(f"{type(e).__name__}: {e}")
                continue
            latencias.append((time.perf_counter() - t0) * 1000)
            total += 1
            acertos_depto += decisao["departamento"] == t["departamento"]
            acertos_urg += decisao["urgente"] == t["urgente"]
            tokens_in += uso.get("input_tokens", uso.get("prompt_tokens", 0))
            tokens_out += uso.get("output_tokens", uso.get("completion_tokens", 0))

    chamadas = len(TICKETS) * args.repeticoes
    if not total:
        raise SystemExit(f"nenhuma chamada válida. Primeiros erros: {(erros_http + erros)[:3]}")
    resumo = {
        "modelo": args.modelo,
        "chamadas": chamadas,
        "erros_http": len(erros_http),
        "erros_de_contrato": len(erros),
        "latencia_p50_ms": round(statistics.median(latencias), 1),
        "latencia_p95_ms": round(p(latencias, 0.95), 1),
        "acerto_departamento": round(acertos_depto / total, 3),
        "acerto_urgente": round(acertos_urg / total, 3),
        "tokens_entrada_por_chamada": round(tokens_in / total, 1),
        "tokens_saida_por_chamada": round(tokens_out / total, 1),
        "exemplos_de_erro": (erros_http + erros)[:3],
    }
    print(json.dumps(resumo, indent=2, ensure_ascii=False))
    os.makedirs("resultados", exist_ok=True)
    nome = args.modelo.replace("@cf/", "").replace("/", "_") + ("_json-object" if MODO_OBJETO else "")
    with open(f"resultados/{nome}.json", "w", encoding="utf-8") as f:
        json.dump(resumo, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
