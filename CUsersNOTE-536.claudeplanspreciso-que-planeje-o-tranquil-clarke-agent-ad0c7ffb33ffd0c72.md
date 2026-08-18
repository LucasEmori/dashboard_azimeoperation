# Implementation Plan: Multi-Month Dashboard

## Overview
Change architecture to pull all DW data once (parallelized to avoid 150s timeout), compute all months locally in pandas, and export a nested JSON. Update frontend to use any selected month vs YoY.

---

## A. Backend Config & Pipeline (Month Loop)

### 1. `src/config.py`
- Update `ALL_MONTHS` calculation to include **all** months from 2024-01-01 to `TODAY` rather than just 3 previous.
- Keep `set_destaque` but we will loop through all months in `pipeline.py`.

```python
# In set_destaque, after setting DESTAQUE, COMPARACAO_MESES, etc:
# Build ALL_MONTHS as all months from 2024-01 up to DESTAQUE
ALL_MONTHS = []
for y in range(2024, DESTAQUE.year + 1):
    start = 1 if y < DESTAQUE.year else 1
    end = DESTAQUE.month if y == DESTAQUE.year else 12
    for m in range(start, end + 1):
        ALL_MONTHS.append(date(y, m, 1))
```

### 2. `src/pipeline.py`
- Import `concurrent.futures.ThreadPoolExecutor` for parallel DW pulls.
- Pull tables **once per company** (8 total queries: p1/p3/geral x 2 companies + tela3).
- Change `results` structure to nested-by-month:
  ```python
  results = {"meta": _build_meta(), "by_month": {}}
  for d in config.ALL_MONTHS:
      config.set_destaque(d)
      ym = d.strftime("%Y-%m")
      results["by_month"][ym] = {}
      for company in config.COMPANIES:
          # tela1/tela2 use cached dfs; tela3 re-filters raw bronze df
          results["by_month"][ym][company] = {
              "tela1": s1.compute(company, p3, geral),
              "tela2": s2.compute(company, p1),
              "tela3": s3.compute(tela3_raw, d),  # pass month
          }
  ```
- Drop top-level `results["alinare"]` / `results["novitah"]` (legacy) or keep as alias for backward compat with existing `data.json` consumers (e.g., `data.alinare.tela1.destaque` still works by adding `destaque` key pointing to `by_month[meta.destaque_iso[:7]]["alinare"]["tela1"]`).

---

## B. Backend DB Robustness (Parallel, Cursors)

### 1. `src/bq.py`
- **Remove `@lru_cache(maxsize=1)`** from `_conn()`. Connections must be per-thread.
- **Update `query_df`**:
  - Use named server-side cursor: `cur = conn.cursor(name='fetch_cursor')`
  - Use `cur.fetchmany(50000)` in a loop to build DataFrames without memory spikes.
  - Set `conn.autocommit = True` to prevent long-running transactions idling out (Supabase pooler transaction mode dislikes long-lived transactions).
  - Add retry logic that **creates a fresh connection** on `OperationalError` (not reuse cached conn).
- **Split `load_lancamentos_bq` logic**:
  - Query once without filtering: return raw `pd.DataFrame` from bronze.lancamentos.
  - In pipeline loop, call `parse_lancamentos_df(df, d)` where `d` is the current loop month (pass month as parameter instead of relying on global `config.PROXIMO_MES`).
- **Update `parse_lancamentos_df(df, target_month)`** to accept the month parameter.

---

## C. Backend Screen Computes

### 1. `src/screen1.py`
- Fix `unidades_ano_anterior` to correctly calculate based on the specific month passed in via `config.DESTAQUE` (which is set by `set_destaque` in the loop).
- The loop already calls `config.set_destaque(d)` before `s1.compute()`, so `config.DESTAQUE_ANO_PASSADO` is correct for each month. No change needed if we keep global state approach. **Verify**: screen1 uses `config.DESTAQUE_ANO_PASSADO` which `set_destaque` updates. This is correct.

### 2. `src/screen2.py`
- **Fix bug**: Line 38: `yr_filter = p1[p1[data_col].dt.year == config.TODAY.year]` → change to `config.DESTAQUE.year`.
- `config.TODAY` is fixed at import time; `config.DESTAQUE` changes per loop iteration.
- The `ano_anterior` entry uses `config.DESTAQUE_ANO_PASSADO.year` which is correct because `set_destaque` updates it.

### 3. `src/screen3.py`
- `compute(records, target_month)` signature: receive the target month as a parameter instead of implicit `config.PROXIMO_MES`.
- Filter records: `data_val` matches `target_month` OR "Sem data" (Pendente).
- Return dict with `mes` string = `f"{config.month_label(target_month)} {target_month.year}"`.

---

## D. API Status Updates

### 1. `app.py`
- Update `sync_status` dict: `{"state": "idle|syncing", "error": None, "progress": "", "stage": "", "rows": 0}`
- In `_run_pipeline_bg`, pass a progress callback to `pipeline.run(progress_cb=...)`.
- In `pipeline.py` run loop, call `progress_cb("Pulling DB (2/8)...", rows=total_rows)` for UX.

---

## E. Frontend Changes

### 1. `src/App.jsx`
- On load, if `month` is null, set to `meta.destaque_iso[:7]` (current default).
- Add `meta.months` (list of all available YYYY-MM strings) to data for TopBar.

### 2. `src/components/TopBar.jsx`
- Change `meses` array to read from `meta.months` (full list of ~30 months).
- Show sync progress string if `syncing` is true and `meta.progress` exists.

### 3. `src/utils/dataResolver.js`
- Simplify to direct lookup:
  ```js
  export function resolveTelaX(data, company, month, screen) {
    return data.by_month?.[month]?.[company]?.[screen] ?? data[company]?.[screen]?.destaque;
  }
  ```
- Screen2/Screen3 components call `resolveTelaX(data, company, month, "tela2")` etc.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| **JSON Size**: Keeping `notas_detalhe` for ~30 months might bloat `data.json` to 5-10MB | Only keep top 20 fornecedores per month in `sku_por_fornecedor`; or enable FastAPI `GZipMiddleware` for `/api/data` |
| **Memory**: Holding 8 full pandas DataFrames | Drop columns we don't need immediately after `query_df` (e.g., only keep needed columns) |
| **Global state in `config`** (set_destaque modifies globals) | Sequential loop is single-threaded so OK; just ensure compute order is correct |
| **`tela3` "Pendente" rows appearing in every month** | `parse_lancamentos_df(df, target_month)` filters correctly: Pendente rows always in_scope; date rows only if month matches target |

---

## Verification Steps

1. **Local pipeline test**: `DATA_SOURCE=bq python src/pipeline.py`
   - Check `output/data.json` size and structure (`by_month` keys exist, ~30 entries).
   - Verify `meta.months` array contains all YYYY-MM from 2024-01 to current.

2. **Server + UI test**: `python app.py` (port 8501) and `npm run dev` (Vite).
   - Open dashboard, select a month from 2024. Verify data populates and YoY comparison works.
   - Click "Atualizar do DW" and verify it does not timeout (takes < 60s total).
   - Watch `/api/status` progress updates in browser devtools.

3. **Backward compat**: Ensure existing consumers of `data.json` (if any) still see `data.alinare.tela1.destaque` etc. by adding legacy alias keys in `_export`.

---

## File Summary (Critical Files for Implementation)

```
src/config.py          - ALL_MONTHS generation, set_destaque updates
src/pipeline.py        - Main loop, parallel pulls, nested JSON export
src/bq.py              - Per-thread connections, server-side cursors, fetchmany, raw tela3 pull
src/screen2.py         - Fix TODAY.year -> DESTAQUE.year bug
src/screen3.py         - Accept target_month param, filter records per month
src/utils/dataResolver.js - Simplify to by_month lookup
src/components/TopBar.jsx  - Full month list from meta.months
app.py                 - /api/status progress, GZipMiddleware
```

---

## Rejected Approaches (One Line Each)

- **Offset pagination**: Slow on DW, pointless with full sync; rejected.
- **SQL GROUP BY pushdown**: Correct but big refactor of screen1/2 semantics; defer as optimization.
- **CSV intermediate**: JSON suffices; no need.
- **Per-month sync endpoints**: User chose full sync; rejected.
