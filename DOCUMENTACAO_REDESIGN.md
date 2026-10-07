# Commercial Analytics — documentação do redesign

Projeto: `Dashboard Comercial.pbip` · Redesign em 07/10/2026 · Dados de 16/02/2021 a 22/10/2023 (cache local).

## 1. Objetivo

Transformar o relatório "Realizado vs. Meta / Forecast / Recomendações" em uma solução de decisão comercial que responde, em sequência:

| # | Pergunta | Página |
|---|----------|--------|
| 1 | O que aconteceu? | 01 Visão Executiva |
| 2 | Por que aconteceu? | 02 Performance |
| 3 | O que provavelmente vai acontecer? | 03 Forecast |
| 4 | Quais produtos explicam o resultado? | 04 Produtos |
| 5 | Quais clientes explicam o resultado? | 05 Clientes |
| 6 | O que o comercial deve fazer agora? | 06 Next Best Product |

As regras de negócio originais (faturamento, rateio de meta, meta diária, recomendação por similares e por histórico) foram preservadas e validadas número a número (seção 9).

## 2. O que os dados contêm

| Item | Valor |
|------|-------|
| fVendas | 39.960 linhas de item de nota, 3.431 NF-e, 11,7 itens por nota |
| Período | 16/02/2021 a 22/10/2023 (a data da última venda é o "hoje" do relatório) |
| Clientes | 701 cadastrados, 696 com compra; 23 cidades, 17 UFs, 2 regiões |
| Produtos | 93 SKUs (produto + tamanho P/M/G/GG), 25 modelos, 4 categorias |
| Vendedores | 12 vendedores, 5 supervisores, 2 gerentes |
| Metas | 2022 (mensal, CSV) e 2023 (trimestral, Excel), por gerente × categoria, diluídas por dia útil |
| Similaridade | 1.444 pares cliente–similar (até 3 por cliente, 503 clientes com similar); 88 pares produto–similar |

Achados que orientaram o desenho:

- **Vende-se todos os dias da semana em volume parecido** (índice de 0,89 a 1,10), mas a meta é diluída só em dias úteis. Por isso o run rate do forecast usa dias corridos e a comparação de ritmo usa a mesma base da meta (dias úteis).
- **Baixa concentração de clientes**: os 10 maiores somam 7,6% do faturamento de 2023. O risco está em recência, não em dependência.
- **Ciclo de recompra de ~6 meses** (mediana de 5 notas por cliente em 2,7 anos; recência mediana de 123 dias). Os cortes de RFV (180/365 dias) seguem esse ciclo.
- **Alta concentração de produtos**: 15 dos 25 modelos somam 80% do faturamento; "Incomparaveis" responde por 15,9% e cresce abaixo da média.
- **O forecast original não era projeção**: somava ao realizado a meta dos dias restantes, portanto sempre convergia para a meta.

## 3. Arquitetura do modelo

Star schema preservado: `fVendas` → `dCalendario`, `dCliente`, `dProduto`, `dVendedor`; `fMetas` → `dCalendario` (e N:N com `dProduto[categoria_id]` e `dVendedor[gerente_id]`, mantido porque o rateio da meta depende dele).

Objetos novos:

| Objeto | Tipo | Função |
|--------|------|--------|
| `dCalendario[Ano Seleção]`, `[Mês Seleção]` | Colunas calculadas | "Ano Atual" / "Mês Atual" ancorados na última venda. Substituem `AnoAtual`/`MesAtual`, que dependiam do relógio do sistema no Power Query e quebrariam em qualquer atualização feita depois de 2023 |
| `dCalendario[Dia]`, `[DiaUtil]`, `[Mês Ref]` | Colunas calculadas | Apoio a forecast e dias úteis |
| `dCliente[Primeira Compra]`, `[Última Compra]`, `[Recência (dias)]`, `[Pedidos 12M]`, `[Faturamento 12M]`, `[Segmento RFV]` | Colunas calculadas | Foto RFV na data da última venda |
| `pSegmento` | Tabela calculada + relacionamento com `dCliente[Segmento RFV]` | Ordem dos segmentos e ação sugerida |
| `pForecast` | Parâmetro desconectado | Método de forecast |
| `pRanking` | Parâmetro desconectado | Recorte do ranking de vendedores |
| `pMétrica`, `pDimensão` | Field parameters | Métrica e dimensão de quebra |
| `dProdutoBase` | Tabela calculada desconectada | Produto âncora da análise de afinidade |

Removidos: tabela `auxUX` e 50 medidas antigas (todas preservadas em `_backup_2026-10-07_original`). Mantidos sem uso no relatório: `auxVisao` (calculation group YTD / por Mês), `auxGerenteSupervisor` e `fSimilaridadeProdutos`.

## 4. Medidas (174, em pastas)

| Pasta | Conteúdo |
|-------|----------|
| 00 Base | Faturamento, Quantidade, Pedidos, Clientes, Ticket Médio, Preço Médio, Custo, Margem, Desconto, Data Última Venda |
| 02 Metas | Meta, Meta até Hoje, Gap Meta, Gap Meta %, Atingimento % (+ Rateio: Meta Base, Fator Produto, Fator Vendedor) |
| 03 Comparações | Faturamento LY, YoY %, YoY Δ, Faturamento LM, MoM %, e LY/YoY de Pedidos, Ticket, Quantidade e Clientes |
| 04 Forecast | Forecast, Forecast Plano, Forecast x Meta, Atingimento Forecast %, dias corridos e úteis, ritmo, curvas acumuladas, índices sazonais |
| 05 Produtos | Participação, Rank, Pareto, Classe ABC, Share Top 10, Penetração, Contribuição, Quadrante, Afinidade |
| 06 Clientes | Novos, Recorrentes, Sem Recompra, Concentração, foto RFV 12M |
| 07 Recomendação | Perfil, Similares, Next Best Product, Recompra |
| 08 Ranking | Rank Vendedor, Status Meta, Filtro Ranking |
| 09 UX | Títulos, Rótulos, Cores e Insights textuais |

Convenções:

- **Meta até Hoje** = meta acumulada até a última venda. Todo "atingimento" e "gap" do realizado usa essa base; a meta cheia do período só aparece no forecast.
- **Comparações (LY/LM)** são like-for-like: limitadas à janela já realizada.
- **Dynamic format strings** em Faturamento, Meta, Gap, Forecast e derivados: `R$ 2,55 Mi`, `R$ 373,5 mil`, `R$ 8.840`.
- Rankings e Pareto usam `CALCULATETABLE(..., ALLSELECTED(dimensão))`, por isso não mudam quando o visual ganha outra coluna da mesma dimensão.

## 5. Forecast

`Forecast = Faturamento + Forecast Restante`, em que a parte restante projeta só os dias depois da última venda, pelo método escolhido em `pForecast`:

| Método | Como projeta os dias restantes |
|--------|-------------------------------|
| Adaptativo (padrão) | `peso × Run Rate + (1 − peso) × Sazonal`, com `peso = dia do mês ÷ dias do mês` |
| Run Rate | Média diária (dias corridos) do mês em andamento |
| Média Móvel 28d | Média diária das últimas 4 semanas |
| Sazonal | Mesmos dias do ano anterior × crescimento dos últimos 90 dias |
| Plano de Metas | Método original: meta dos dias restantes |

Backtest (19 meses, de mar/2022 a set/2023, projetando no dia 22 de cada mês):

| Método | Erro médio absoluto | Viés |
|--------|--------------------:|-----:|
| Adaptativo | 9,7% | +1,1% |
| Run Rate | 10,6% | +0,4% |
| Sazonal | 10,8% | +2,6% |
| Média Móvel 28d | 10,9% | +0,7% |
| Plano de Metas (original) | 15,0% | +3,1% |

Para outubro/2023 (meta de R$ 373,5 mil, realizado de R$ 234,3 mil até 22/10):

| Método | Forecast | % da meta |
|--------|---------:|----------:|
| Adaptativo | R$ 320,6 mil | 85,8% |
| Run Rate | R$ 330,1 mil | 88,4% |
| Média Móvel 28d | R$ 329,8 mil | 88,3% |
| Sazonal | R$ 297,1 mil | 79,5% |
| Plano de Metas (original) | R$ 353,1 mil | 94,6% |

São heurísticas de ritmo e sazonalidade, não um modelo estatístico; não há intervalo de confiança.

**Ritmo**: Meta Diária Original = meta ÷ dias úteis (R$ 16.977); Meta Diária Necessária = (meta − realizado) ÷ dias úteis restantes (R$ 19.885); Realizado Diário Médio = realizado ÷ dias úteis decorridos (R$ 15.620). Dias úteis = segunda a sexta, sem feriados, a mesma regra usada na diluição das metas.

## 6. Recomendação

**Clientes similares** (lógica original, mantida): no Power Query, um script Python monta a matriz cliente × SKU com a quantidade comprada no ano corrente e calcula a similaridade de cosseno; ficam os 3 mais parecidos de cada cliente com similaridade entre 0,50 e 0,99.

**Next Best Product**: produtos que os similares compraram no período e o cliente não.

`Score Recomendação = 100 × (0,75 × penetração ponderada nos similares + 0,25 × penetração na base ativa)`

- Penetração ponderada: soma da similaridade dos similares que compraram ÷ soma da similaridade de todos os similares.
- É um score heurístico de ordenação (0 a 100), não uma probabilidade de compra. Leituras: Alta ≥ 70, Média ≥ 40, Exploratória abaixo disso.
- `Qtd Recomendada Similares` reproduz a medida original.

**Recompra**: itens do histórico do cliente sem compra no período (`Qtd Recompra Sugerida`, igual à original).

**Afinidade** (página Produtos): dos clientes que compraram o produto âncora, o percentual que também comprou cada outro produto, e o lift sobre a penetração geral.

**Segmentação RFV** (regras, não cluster): Inativos > 365 dias sem compra · Em risco 181–365 · Novos (primeira compra há menos de 180 dias) · VIP (3+ notas em 12M e faturamento no quartil superior) · Leais (2+ notas) · Potencial (1 nota). Distribuição: 99 VIP, 225 Leais, 114 Potencial, 9 Novos, 135 Em risco, 114 Inativos.

## 7. Design system

Tema único em `StaticResources/RegisteredResources/CommercialAnalyticsDark.json`; os visuais só carregam exceções.

| Token | Hex | Uso |
|-------|-----|-----|
| BG | `#111827` | Fundo da página |
| BG2 | `#182033` | Superfície dos visuais e rail |
| SURFACE | `#202A44` | Slicers, hover |
| ELEVATED | `#27324F` | Tooltips |
| PURPLE | `#6957FF` | Primária: realizado, foco, página ativa |
| PURPLE2 | `#8B5CF6` | Acento |
| CYAN | `#22C7BE` | Forecast, destaque secundário |
| GREEN / AMBER / CORAL | `#39D98A` / `#F5B942` / `#FF7A68` | Acima da meta / atenção / abaixo |
| MUTED | `#6B7694` | Referência (meta, médias) |
| TEXT / TEXT2 | `#F8FAFC` / `#AEB8CF` | Texto principal / secundário |

Grid: canvas 1440 × 810 (16:9), rail de 168 px, margens de 24 px, espaçamento de 16 px, raio de 12 px, sem sombras. Tipografia Segoe UI: título de página 22, KPI 17, título de visual 11, corpo 9–10.

Acessibilidade: todo status tem símbolo além da cor (▲ ▼ ●), alt text nos visuais principais, ordem de tabulação na ordem de leitura, contraste de texto acima de 7:1 sobre as superfícies.

## 8. Páginas

| Página | Conteúdo |
|--------|----------|
| 01 Visão Executiva | 7 KPIs com comparação, curva acumulada realizado × meta × forecast com marcador da última venda, status da meta, leitura executiva (5 frases dinâmicas), realizado × meta por mês |
| 02 Performance | Variance bar mensal (meta como marcador), contribuição ao crescimento por dimensão (field parameter), ranking de vendedores com barras, sparkline, status e recortes (Todos, Acima, Abaixo, Top, Em risco) |
| 03 Forecast | 8 KPIs, curva acumulada com projeção tracejada, ritmo diário, comparação dos 5 métodos contra a meta, sazonalidade mensal e por dia da semana |
| 04 Produtos | Matriz de performance (participação × crescimento), Pareto com classe ABC, tabela de crescimento e penetração, afinidade com produto âncora |
| 05 Clientes | KPIs de base, segmentos RFV com ação sugerida, recência × valor, clientes do período, faturamento por segmento |
| 06 Next Best Product | Cliente → histórico → similares e perfil → ranking de recomendação → ação comercial |
| Tooltips | Produto, Vendedor e Cliente |

Filtros: barra compacta superior (Ano, Mês, Gerente, Categoria). Ano, Gerente e Categoria são sincronizados entre páginas; o Mês abre em "Mês Atual" no Forecast e em "Todos" nas demais. Não há bookmarks.

## 9. Validação antes × depois

| Indicador (contexto) | Original | Novo |
|----------------------|---------:|-----:|
| Faturamento (2023 até 22/10) | 2.545.609 | 2.545.609 |
| Meta até a última venda (2023) | 2.701.154 | 2.701.154 |
| Faturamento vs meta (2023) | −155.545 | −155.545 |
| Faturamento YoY (2023) | +26,6% | +26,6% |
| Notas emitidas (2023) | 1.075 | 1.075 |
| Notas YoY | +39,4% | +39,4% |
| Ticket médio (2023) | 2.368 | 2.368 |
| Ticket YoY | −9,2% | −9,2% |
| Faturamento (out/2023) | 234.298 | 234.298 |
| Meta do mês (out/2023) | 373.492 | 373.492 |
| Forecast MTD original (out/2023) | 353.137 | 353.137 (`Forecast Plano`) |
| Forecast YTD original (2023) | 3.394.455 | 3.394.455 (`Forecast Plano`) |
| Meta diária original | 16.977 | 16.977 |
| Meta diária necessária | 19.885 | 19.885 |
| Dias úteis / realizados (out/2023) | 22 / 15 | 22 / 15 |
| Meta de Bruna Maria (2023) | 228.718 | 228.718 |
| Recomendados por similares, Bailey Inc, out/2023 | 124 itens | 124 itens |
| Recomendados por histórico, Bailey Inc, out/2023 | 172 itens | 172 itens |
| 2022 · Bruna Maria · Manga Curta: faturamento / meta | 127.384 / 96.686 | 127.384 / 96.686 |

Mudança intencional: o forecast em destaque passa a ser o Adaptativo (R$ 320,6 mil em out/2023; R$ 3,30 Mi no ano), não o Plano de Metas (R$ 353,1 mil; R$ 3,39 Mi). O método original continua disponível no seletor.

## 10. Power Query — auditoria (sem alterações)

As consultas não foram alteradas porque as fontes não estão acessíveis nesta máquina e qualquer mudança só poderia ser validada com uma atualização.

| Ponto | Situação | Recomendação |
|-------|----------|--------------|
| Caminhos fixos `G:\Drives compartilhados\...` em Metas e Fotos | Atualização só funciona na máquina de origem | Parâmetro `PastaDados` |
| `similaridade_clientes` / `similaridade_produtos` filtram `Date.IsInCurrentYear` | Em 2026 o filtro devolve zero linhas e as tabelas de similaridade ficam vazias | Filtrar pelo ano da última venda ou por janela móvel de 12 meses |
| `dCalendario[Passado]`, `AnoAtual`, `MesAtual` | `AnoAtual`/`MesAtual` usam o relógio do sistema | Já substituídas no relatório por colunas DAX; remover do M na próxima atualização |
| As duas consultas de similaridade releem `dbo.fVendas` | Fonte lida 3 vezes | Referenciar a consulta `fVendas` |
| `fMetas2023` depende do layout da planilha (cabeçalho "1 - Victor Castro") | Frágil a mudança de layout | Padronizar a planilha de metas |
| `fRecomendacoes` | Calculada no Python e não carregada | Remover ou carregar; a recomendação do relatório é feita em DAX |
| `fVendas[dia da semana]` | Coluna calculada duplicando `dCalendario[DiaSemana]` | Remover |

## 11. Como regenerar o relatório

A pasta `_build` contém o gerador das páginas (Python 3, sem dependências):

```
python _build/build.py
```

- `tokens.py`: cores, grid e tema. `components.py`: rail, cabeçalho, slicers, KPIs, gráficos. `pages.py`: as páginas. `pbir.py`: utilitários PBIR.
- Rodar com o Power BI Desktop fechado. O gerador sobrescreve `Dashboard Comercial.Report/definition/pages` e o tema; ajustes feitos à mão no Desktop nessas páginas são perdidos.
- `add_measures.py` e `fix_measures.py` registram as edições feitas no TMDL depois do primeiro salvamento.

## 12. Evolução sugerida

1. Corrigir as consultas de similaridade (item 10) e atualizar os dados.
2. Dimensões `dCategoria` e `dGerente` para trocar os relacionamentos N:N de `fMetas` por 1:N.
3. Calendário de feriados para os dias úteis.
4. Meta por vendedor ponderada pelo histórico, em vez de divisão igualitária.
5. Score de recomendação com recência e margem do produto.
6. RLS por gerente.
