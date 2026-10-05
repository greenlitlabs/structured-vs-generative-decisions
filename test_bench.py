import pytest

import bench
from tickets import DEPARTAMENTOS, TICKETS


def test_tickets_bem_formados():
    assert len(TICKETS) == 24
    for t in TICKETS:
        assert t["departamento"] in DEPARTAMENTOS
        assert isinstance(t["urgente"], bool)


def test_decidir_clef_aplica_limiar_e_nivel(monkeypatch):
    resposta = {
        "answers": {
            "departamento": {"choice": "tecnico"},
            "urgente": {"noul": 0.9715},
            "frustracao": {"score": 1.2},
        },
        "usage": {"input_tokens": 356, "output_tokens": 0},
    }
    monkeypatch.setattr(bench, "post", lambda modelo, corpo: resposta)
    decisao, uso = bench.decidir_clef("@cf/cloudflare/clef", "ticket")
    assert decisao == {"departamento": "tecnico", "urgente": True, "frustracao": "incomodado"}
    assert uso["input_tokens"] == 356


def test_decidir_clef_usa_nome_curto_do_modelo(monkeypatch):
    corpos = []
    resposta = {
        "answers": {"departamento": {"choice": "conta"}, "urgente": {"noul": 0.1},
                    "frustracao": {"score": 0}},
        "usage": {},
    }
    monkeypatch.setattr(bench, "post", lambda m, c: corpos.append(c) or resposta)
    bench.decidir_clef("@cf/cloudflare/clef-flash", "ticket")
    assert corpos[0]["model"] == "clef-flash"


def _generativo(monkeypatch, saida):
    monkeypatch.setattr(bench, "post", lambda m, c: {"response": saida, "usage": {}})


def test_generativo_aceita_contrato_valido(monkeypatch):
    _generativo(monkeypatch, '{"departamento": "conta", "urgente": false, "frustracao": "calmo"}')
    decisao, _ = bench.decidir_generativo("modelo", "ticket")
    assert decisao["departamento"] == "conta"


@pytest.mark.parametrize("saida", [
    {"departamento": "vendas", "urgente": True, "frustracao": "calmo"},
    {"departamento": "conta", "urgente": "sim", "frustracao": "calmo"},
    {"departamento": "conta", "urgente": True, "frustracao": "furioso"},
])
def test_generativo_rejeita_fora_do_contrato(monkeypatch, saida):
    _generativo(monkeypatch, saida)
    with pytest.raises(ValueError):
        bench.decidir_generativo("modelo", "ticket")


def test_percentil():
    assert bench.p([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 0.95) == 10
    assert bench.p([5], 0.95) == 5
