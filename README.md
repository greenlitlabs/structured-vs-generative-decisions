# structured-vs-generative-decisions

Código do artigo "Decisão tipada com probabilidade: Jev, Clef e o que medimos", da Greenlit Labs.

Compara o Clef (decisão tipada, Cloudflare Workers AI) com dois LLMs generativos com JSON mode em 24 tickets de suporte rotulados à mão, e mede quanto dá para automatizar usando a probabilidade como limiar de certeza.

## Rodar

Requer Python 3.10+, sem dependências além da biblioteca padrão (testes usam `pytest`).

```bash
export CLOUDFLARE_ACCOUNT_ID=...
export CLOUDFLARE_API_TOKEN=...   # token com permissão Workers AI

python bench.py @cf/cloudflare/clef
python bench.py @cf/cloudflare/clef-flash
python bench.py @cf/meta/llama-3.3-70b-instruct-fp8-fast
python bench.py @cf/meta/llama-3.1-8b-instruct-fp8 --json-object   # sem suporte a json_schema

python calibracao.py @cf/cloudflare/clef
python calibracao.py @cf/cloudflare/clef-flash

pip install pytest && python -m pytest   # não chama a API
```

`probe.py` faz uma chamada ao Clef e lista os modelos de texto disponíveis, só para ver o formato real da resposta.

## Arquivos

- `tickets.py`: os 24 tickets e as categorias.
- `bench.py`: latência, acerto e tokens por modelo (3 repetições por ticket).
- `calibracao.py`: acerto por limiar de certeza na pergunta de urgência.
- `resultados/`: saídas medidas, as mesmas citadas no artigo.

## Resultados medidos

24 tickets x 3 repetições, cliente no Brasil pela internet. A latência inclui a rede.

| modelo | p50 | p95 | acerto depto | acerto urgência | tokens entrada/saída |
|---|---|---|---|---|---|
| Clef | 704 ms | 1382 ms | 1,00 | 0,80 | 356 / 0 |
| Clef-flash | 575 ms | 1084 ms | 1,00 | 0,88 | 356 / 0 |
| Llama 3.3 70B (`json_schema`) | 1118 ms | 2665 ms | 1,00 | 0,67 | 164 / 27 |
| Llama 3.1 8B (`json_object`) | 2042 ms | 2869 ms | 1,00 | 0,79 | 174 / 31 |

Calibração (Clef, pergunta de urgência): com certeza mínima de 0,9, 17 de 24 tickets são decididos com 100% de acerto e 7 vão para uma pessoa.

## Limites

- 24 tickets e rótulos do autor: diferenças de acerto de urgência não formam ranking.
- Os limiares foram escolhidos nos mesmos tickets em que foram medidos. Use um lote separado para o seu caso.
- O Jev (TypeSafe) não foi medido, apenas o Clef e os baselines. A interface compatível deve permitir trocar URL e chave.
- Os valores de latência de servidor e de benchmark publicados pela Cloudflare não foram verificados aqui.
