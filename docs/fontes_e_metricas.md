# Dashboard Alinare & Novitah — Explicativo de Fontes e Métricas

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [As Planilhas (Fontes de Dados)](#2-as-planilhas-fontes-de-dados)
3. [Tela 1 — Notas de Entrada](#3-tela-1--notas-de-entrada)
4. [Tela 2 — Produtos Lançados](#4-tela-2--produtos-lançados)
5. [Tela 3 — Próximos Lançamentos](#5-tela-3--próximos-lançamentos)
6. [Períodos: Destaque, Comparação e Planejamento](#6-períodos-destaque-comparação-e-planejamento)

---

## 1. Visão Geral

O dashboard consolida dados de **duas empresas** (Alinare e Novitah) em **três telas** cada, com informações sobre notas fiscais de entrada, lançamentos de produtos e programação futura.

**Fluxo dos dados:**
1. As planilhas Excel são preenchidas manualmente pela equipe
2. Um processamento automático lê essas planilhas, cruza as informações e gera um arquivo JSON
3. O dashboard (site) lê esse JSON e exibe os indicadores e gráficos

---

## 2. As Planilhas (Fontes de Dados)

Cada empresa tem **três arquivos** na pasta `data/`. Veja o que cada um contém:

### Produtos Lançados (P1)

**Arquivo:** `1 - produtos lançados*.xlsx` (mesmo nome para ambas empresas)

**Aba usada:** `Plan1`

**O que tem:** registro de todos os lançamentos de produto. Cada linha é um item lançado.

| Coluna | O que significa |
|--------|----------------|
| `Lançamento` | Número do lote |
| `Item` | Sequência dentro do lote |
| `Sequência` | Ordem |
| `Produto` | Código do produto (SKU) |
| `Descrição` | Nome do produto |
| `Qtd. Transferida` | Quantidade transferida |
| `Data` | Data do lançamento |
| `Data Lançamento` | Data em que o lançamento foi efetivado (coluna H) |
| `Data Virada` | Data de virada |

### Notas de Entrada (P3)

**Arquivo:** `3 - Notas de entrada*.xlsx`

**Aba usada:** `Plan1`

**O que tem:** todas as notas fiscais de entrada (compra) registradas.

| Coluna | O que significa |
|--------|----------------|
| `Número` | Número da nota fiscal |
| `Data Entrada` | Data de entrada da NF no sistema |
| `Data Emissão` | Data de emissão da NF |
| `Razão Social` | Nome do fornecedor |
| `Valor Total` | Valor total da nota |

### Geral / Estoque (P2)

**Arquivo:** `2 - PLANILHA GERAL*.xlsx`

**Aba usada no Alinare:** `Geral`
**Aba usada na Novitah:** `BASE GERAL`

**O que tem:** informações de estoque, produtos, quantidades, fornecedores.

**Atenção:** as colunas têm nomes diferentes entre as duas empresas:

| Informação | Nome na coluna da Alinare | Nome na coluna da Novitah |
|-----------|--------------------------|--------------------------|
| Código do produto | `COD PROD` | `COD BARRAS` |
| Quantidade recebida | `QUANTIDADE` | `Quantidade` |
| Número da NF | `NF` | `NF` |
| Fornecedor | `FORNECEDOR` | `FORNECEDOR` (com espaço no final) |
| Marca | `MARCA` | `MARCA` |

### Aba de Próximos Lançamentos

Essa aba fica **dentro do arquivo P2 da Alinare** em uma aba separada chamada `Lancamentos`.

**O que tem:** itens programados para lançamento nos próximos meses.

| Coluna | O que significa |
|--------|----------------|
| B | BU (unidade de negócio): "alinare" ou "novitah" |
| C | Data prevista ou "Pendente" |
| D | Descrição do produto |
| E | Data de embarque |
| F | Status do marketing (MKT) |
| G | Status ("Programado", "Finalizado", "Lançado" ou outro) |

---

## 3. Tela 1 — Notas de Entrada

### 3.1. Notas Emitidas (card em destaque)

- **Fonte:** planilha P3 (Notas de Entrada)
- **Coluna usada:** `Data Entrada`
- **Como calcula:** conta quantas linhas (notas fiscais) existem no mês em destaque.
- **Exemplo:** se o mês destaque é Junho/2026, conta todas as NFs com Data Entrada em Junho/2026.

### 3.2. Total de SKUs Únicos (card)

- **Fonte:** planilha P3 + planilha Geral (P2)
- **Colunas usadas:**
  - P3: `Número` da NF
  - Geral: `NF` e `COD PROD` (ou `COD BARRAS` na Novitah)
- **Como calcula:**
  1. Pega os números das NFs do mês destaque (vindas do P3)
  2. Para cada NF, busca na planilha Geral quantos produtos diferentes (SKUs distintos) aquela NF contém
  3. Soma todos os SKUs de todas as NFs do mês

### 3.3. SKU/Nota (média) — subtexto do card acima

- **Fonte:** mesmo cálculo acima
- **Como calcula:** divide o `Total de SKUs Únicos` pelo `Número de Notas Emitidas`

### 3.4. Top Fornecedor (card)

- **Fonte:** planilha P3 + planilha Geral
- **Colunas usadas:**
  - P3: `Razão Social`
  - Geral: `COD PROD`
- **Como calcula:**
  1. Para cada NF do mês destaque, descobre quantos SKUs ela tem
  2. Agrupa os SKUs por fornecedor (Razão Social)
  3. Mostra o fornecedor com a maior quantidade de SKUs
  4. O número abaixo é a quantidade de SKUs desse fornecedor

### 3.5. Unidades Recebidas (card)

- **Fonte:** planilha P3 + planilha Geral
- **Colunas usadas:**
  - P3: `Número` da NF
  - Geral: `NF` e `QUANTIDADE` (ou `Quantidade` na Novitah)
- **Como calcula:**
  1. Pega as NFs do mês destaque
  2. Busca na planilha Geral a soma da coluna `QUANTIDADE` para essas NFs
  3. Mostra o total de unidades recebidas

### 3.6. Gráfico 1 — Unidades Recebidas por Mês do Trimestre

- **Tipo:** gráfico de barras
- **Fonte:** P3 + Geral
- **Como calcula:**
  1. O usuário seleciona um trimestre (1º trim., 2º trim., etc.)
  2. O gráfico mostra 3 barras, uma para cada mês daquele trimestre
  3. Cada barra é o total de Unidades Recebidas naquele mês
- **Observação:** só aparecem trimestres com os 3 meses completos (com dados)

### 3.7. Gráfico 2 — Comparativo Trimestral

- **Tipo:** gráfico de barras
- **Fonte:** P3 + Geral
- **Como calcula:**
  1. Soma todas as Unidades Recebidas de cada trimestre completo
  2. Mostra uma barra para cada trimestre (T1, T2, etc.)
  3. Permite comparar o volume recebido entre os trimestres do ano

---

## 4. Tela 2 — Produtos Lançados

**Toda a Tela 2 usa apenas a planilha P1** (Produtos Lançados).

### 4.1. Média de Prazo (card em destaque, colorido)

- **Fonte:** P1
- **Colunas usadas:** `Data` e `Data Lançamento`
- **Como calcula:**
  1. Para cada linha do mês destaque, calcula a diferença em dias entre `Data Lançamento` e `Data`
  2. Remove os valores negativos (quando a data de lançamento é anterior à data base)
  3. Tira a média dos dias restantes
  4. Exibe no formato "+X dias"
- **Cor:** verde se a média for positiva, vermelha se negativa

### 4.2. SKU's Únicos (card)

- **Fonte:** P1
- **Coluna usada:** `Produto`
- **Como calcula:** conta quantos produtos diferentes (códigos únicos) existem no mês destaque

### 4.3. Dia de Pico (card)

- **Fonte:** P1
- **Coluna usada:** `Data`
- **Como calcula:**
  1. Agrupa os lançamentos por dia
  2. Descobre qual dia teve a maior quantidade de lançamentos
  3. Mostra a data e o dia da semana

### 4.4. Lançamentos Realizados (card)

- **Fonte:** P1
- **Coluna usada:** `Data Lançamento` (coluna H)
- **Como calcula:**
  1. Filtra apenas as linhas onde `Data Lançamento` está no mês destaque
  2. Agrupa por data e conta quantas linhas cada data tem
  3. Considera "lançamento realizado" todo dia que tiver **30 ou mais linhas**
  4. Mostra quantos dias atingiram esse mínimo

### 4.5. Bloco Comparativo Ano a Ano (YoY)

- **Fonte:** P1
- **O que mostra:** compara o mês destaque (ex: Junho/2026) com o mesmo mês do ano anterior (Junho/2025)

São 3 cartões lado a lado:

| Cartão | Métrica atual | vs | Métrica ano anterior |
|--------|--------------|----|---------------------|
| **SKU's Únicos** | SKUs em Junho/2026 | × | SKUs em Junho/2025 |
| **Lançamentos Realizados** | Dias ≥30 em Junho/2026 | × | Dias ≥30 em Junho/2025 |
| **Média de Prazo** | Média em Junho/2026 | × | Média em Junho/2025 |

Cada cartão mostra o valor atual, o valor do ano anterior e a variação percentual (▲ aumento ou ▼ queda).

### 4.6. Cartões de Comparação (meses anteriores)

Mostra 3 ou 4 cartões com os meses anteriores ao destaque:

| Cartão | Informações exibidas |
|--------|---------------------|
| **Março/2026** | Lançamentos Realizados, Média de Prazo |
| **Abril/2026** | Lançamentos Realizados, Média de Prazo |
| **Maio/2026** | Lançamentos Realizados, Média de Prazo |
| **Junho/2025** (tracejado) | Lançamentos Realizados, SKUs, Média de Prazo |

### 4.7. Gráfico de Volume Acumulado de Lançamentos

- **Tipo:** gráfico de linhas com área preenchida
- **Fonte:** P1
- **Coluna usada:** `Data`

**Como calcula:**
1. Para cada dia do mês (1 a 31), conta quantos lançamentos ocorreram naquele dia
2. Calcula a **soma acumulada** — ou seja, no dia 5 mostra o total de lançamentos do dia 1 ao dia 5
3. Desenha **duas curvas:**
   - **Linha sólida:** mês atual (ex: Junho/2026)
   - **Linha tracejada:** mesmo mês do ano anterior (ex: Junho/2025)
4. A área entre as curvas é preenchida para facilitar a comparação visual
5. Passando o mouse sobre um dia, mostra quantos lançamentos aconteceram naquele dia e o total acumulado até ali

---

## 5. Tela 3 — Próximos Lançamentos

**Fonte exclusiva:** aba `Lancamentos` dentro da planilha P2 da Alinare.

**Filtro inicial:** só aparecem itens do **próximo mês** (ex: se hoje é Julho/2026, mostra itens de Julho/2026) ou itens marcados como **"Pendente"**.

### 5.1. Itens Programados (card em destaque)

- **Fonte:** aba Lancamentos
- **Como calcula:** conta todos os itens que atendem ao filtro (próximo mês ou Pendente), separados por empresa

### 5.2. Status OK (card verde)

- **Fonte:** aba Lancamentos, coluna G (Status)
- **Como calcula:** conta itens onde o status contém as palavras:
  - "Programado", "Finalizado" ou "Lançado"
- **Regra:** se conter qualquer uma dessas → considerado **OK** (pronto)

### 5.3. Em Processo (card vermelho se > 0)

- **Fonte:** mesma coluna G (Status)
- **Como calcula:** conta itens onde o status **não** contém nenhuma das palavras acima
- **Exemplos:** "Em andamento", "Aprovado", etc.

### 5.4. MKT Enviado (card)

- **Fonte:** aba Lancamentos, coluna F (MKT)
- **Como calcula:** conta itens onde a célula de MKT contém a palavra **"entregue"**
- O subtexto mostra quantos estão pendentes

### 5.5. Lista de Itens Programados

- Uma lista com todos os itens, cada um mostrando:
  - Nome do produto
  - Data prevista (ou "Sem data" se for Pendente)
  - Data de embarque
  - **Badge de status:** "Pronto" (verde) ou "Em processo" (amarelo)
  - **Badge de MKT:** "MKT enviado" (verde) ou "MKT pendente" (amarelo)
- A lista é ordenada pela data (mais próximo primeiro)

### 5.6. Total do Mês

- Um cartão na parte inferior mostrando:
  - **Total:** X itens programados
  - **Detalhamento:** Y prontos + Z em processo

---

## 6. Períodos: Destaque, Comparação e Planejamento

O dashboard trabalha com **4 períodos**, calculados automaticamente a partir da data atual:

### Mês Destaque
- **É sempre o mês anterior ao mês atual**
- Exemplo: se hoje é 23 de Julho de 2026 → **Junho de 2026** é o destaque
- Todos os KPIs principais da Tela 1 e Tela 2 são desse mês

### Meses de Comparação
- São os **3 meses anteriores ao mês destaque**
- Exemplo: se destaque é Junho/2026 → **Março, Abril, Maio de 2026**
- Aparecem nos cartões de comparação da Tela 2

### Ano Anterior
- **Mesmo mês do destaque, mas no ano anterior**
- Exemplo: se destaque é Junho/2026 → **Junho de 2025**
- Usado no bloco YoY (comparativo ano a ano) e no gráfico de volume acumulado

### Próximo Mês (Planejamento)
- **É o mês atual do sistema**
- Exemplo: se hoje é Julho/2026 → **Julho de 2026**
- Usado na Tela 3 (Próximos Lançamentos) para filtrar itens programados

---

## Observações Importantes

1. **União entre P3 e Geral:** a ligação entre Notas de Entrada e Estoque é feita pelo número da NF. O sistema extrai apenas os dígitos do número (ignora letras, traços, zeros à esquerda) para fazer a correspondência

2. **Diferença Alinare vs Novitah:** a planilha Geral da Novitah tem nomes de colunas diferentes. O sistema automaticamente:
   - Renomeia `COD BARRAS` para `COD PROD`
   - Localiza `Quantidade` (com Q minúsculo) e trata como `QUANTIDADE`
   - Remove espaços extras do nome do fornecedor

3. **Dias de prazo negativos:** na Tela 2, quando a `Data Lançamento` é anterior à `Data` (prazo negativo), esses registros são removidos do cálculo da média para não distorcer o resultado

4. **Lançamentos Realizados:** o critério de 30 linhas por dia pode ser ajustado se necessário

5. **Gráficos trimestrais:** só aparecem trimestres que têm dados completos nos 3 meses

6. **Itens Pendentes na Tela 3:** itens sem data definida (marcados como "Pendente") são incluídos na lista mesmo sem prazo
