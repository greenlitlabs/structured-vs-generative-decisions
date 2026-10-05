"""Uma chamada ao Clef e uma ao catálogo, só para ver o formato real da resposta.

Uso: python probe.py
Lê CLOUDFLARE_ACCOUNT_ID e CLOUDFLARE_API_TOKEN do ambiente.
"""
import json
import os
import urllib.request

ACCOUNT = os.environ["CLOUDFLARE_ACCOUNT_ID"]
TOKEN = os.environ["CLOUDFLARE_API_TOKEN"]
BASE = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/ai"


def chamar(url: str, corpo: dict | None = None) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(corpo).encode() if corpo is not None else None,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


TICKET = "O checkout está falhando para todos os clientes há uma hora e já perdemos vendas."

corpo = {
    "model": "clef",
    "state": TICKET,
    "questions": {
        "departamento": {
            "type": "choice",
            "instructions": "Qual departamento deve receber este ticket?",
            "criteria": {
                "cobranca": "Pagamento, fatura, reembolso",
                "tecnico": "Falha, erro, indisponibilidade",
                "conta": "Login, senha, cadastro",
            },
        },
        "urgente": {"type": "noul", "instructions": "O ticket é urgente?"},
        "frustracao": {
            "type": "score",
            "instructions": "Quão frustrado está o cliente?",
            "criteria": ["calmo", "incomodado", "irritado"],
        },
    },
}

print("== clef ==")
print(json.dumps(chamar(f"{BASE}/run/@cf/cloudflare/clef", corpo), indent=2, ensure_ascii=False))

print("== modelos de texto disponíveis ==")
catalogo = chamar(f"{BASE}/models/search?per_page=100&task=Text%20Generation")
for m in catalogo["result"]:
    print(m["name"])
