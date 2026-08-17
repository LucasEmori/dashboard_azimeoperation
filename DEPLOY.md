# Deploy no Railway

Dashboard Alinare & Novitah (Streamlit). Container Docker no Railway.

## Como o app funciona em producao

`app.py` le `output/data.json` (ja commitado no repo). **Nao roda pipeline em runtime**
e **nao precisa credencial Supabase no container**. Pipeline (`python -m src.pipeline`)
roda offline na maquina local e o `data.json` resultante e commitado.

Para atualizar dados em producao: rode o pipeline localmente (com
`PG_DSN` configurado) e push do `output/data.json` atualizado.

## Deploy (1 vez)

1. Ir em https://railway.app -> New Project -> Deploy from GitHub repo
2. Selecionar `LucasEmori/dashboard_azimeoperation`
3. Railway detecta `railway.json` + `Dockerfile` automaticamente
4. Settings -> Networking -> Generate Domain (URL publica)
5. Nenhuma variavel de ambiente obrigatoria. Opcional:
   - `DATA_SOURCE` (default `bq`) — so relevante se rodar pipeline no container (nao e o caso)

## Logs / healthcheck

- Healthcheck: `GET /` (Streamlit responde 200)
- Logs: Railway dashboard -> Deployments -> Logs

## Atualizar dados (rotina)

```bash
# local
export PG_DSN="postgresql://postgres.xzoohqiejbuaskpiktfj:azime202600@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"
python -m src.pipeline          # regenera output/data.json
git add output/data.json && git commit -m "data: atualiza data.json" && git push
```

Railway re-deploy automatico a cada push.

Opcional: sobrescrever defaults via env:
- `PG_T2_SOURCE` — `lancamentos` (default) ou `itens_efetivo`
- `PG_SCHEMA` / `PG_T3_SCHEMA` — schemas do DW (defaults: `ouro` / `bronze`)
