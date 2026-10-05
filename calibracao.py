"""A probabilidade do Clef separa os acertos dos erros?

Para cada ticket, pergunta "é urgente?" e guarda a probabilidade (noul).
Depois mede o acerto por faixa de certeza e quanto dá para automatizar
com um limiar de certeza.
Uso: python calibracao.py @cf/cloudflare/clef
"""
import json
import os
import sys

from bench import post
from tickets import TICKETS

LIMIARES = [0.0, 0.7, 0.8, 0.9, 0.95]


def main() -> None:
    modelo = sys.argv[1]
    linhas = []
    for t in TICKETS:
        r = post(modelo, {
            "model": modelo.rsplit("/", 1)[-1],
            "state": t["texto"],
            "questions": {"urgente": {"type": "noul", "instructions": "O ticket é urgente?"}},
        })
        p = r["answers"]["urgente"]["noul"]
        linhas.append({
            "texto": t["texto"], "esperado": t["urgente"], "p_urgente": p,
            "previsto": p >= 0.5, "certeza": max(p, 1 - p),
        })

    print(f"{modelo}\nlimiar_certeza  decididos  acerto_nos_decididos  vao_para_humano")
    faixas = []
    for lim in LIMIARES:
        decididos = [x for x in linhas if x["certeza"] >= lim]
        acertos = sum(x["previsto"] == x["esperado"] for x in decididos)
        acerto = acertos / len(decididos) if decididos else float("nan")
        faixas.append({"limiar": lim, "decididos": len(decididos), "acerto": round(acerto, 3)})
        print(f"{lim:>14}  {len(decididos):>9}  {acerto:>20.3f}  {len(linhas) - len(decididos):>15}")

    print("\nErros:")
    for x in linhas:
        if x["previsto"] != x["esperado"]:
            print(f"  p={x['p_urgente']:.3f} esperado={x['esperado']} :: {x['texto']}")

    os.makedirs("resultados", exist_ok=True)
    nome = modelo.replace("@cf/", "").replace("/", "_")
    with open(f"resultados/calibracao_{nome}.json", "w", encoding="utf-8") as f:
        json.dump({"modelo": modelo, "faixas": faixas, "tickets": linhas}, f,
                  indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
