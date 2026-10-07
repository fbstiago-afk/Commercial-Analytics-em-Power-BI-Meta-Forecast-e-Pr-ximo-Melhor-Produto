# Changelog do redesign — 07/10/2026

Cópia integral do estado anterior em `_backup_2026-10-07_original/`.

## Modelo semântico

| Arquivo | Alteração | Motivo | Antes | Depois | Impacto |
|---------|-----------|--------|-------|--------|---------|
| `tables/Medidas.tmdl` | Medidas recriadas com nomes padronizados e pastas `00`–`09` | Legibilidade, reuso, pastas por assunto | 51 medidas em 9 pastas, prefixos `$`/`%`, textos com FORMAT, erros de digitação | 174 medidas com descrição | Números idênticos (ver validação na documentação) |
| `tables/Medidas.tmdl` | Dynamic format strings em valores monetários | Escala automática sem converter em texto | `R$ 2.545.609` ou medidas-texto | `R$ 2,55 Mi` / `R$ 373,5 mil` | Cartões e tabelas compactos, medidas continuam numéricas |
| `tables/Medidas.tmdl` | `Meta Diária Original/Necessária` numéricas | Eram texto, não podiam ir para gráfico | `"Meta Diária Necessária: R$ 19.885"` | 19.885 | Gráfico de ritmo |
| `tables/Medidas.tmdl` | Forecast com 5 métodos (`pForecast`) | O original somava a meta restante | 1 método | Adaptativo (padrão), Run Rate, Média Móvel, Sazonal, Plano de Metas | Erro do backtest cai de 15,0% para 9,7% |
| `tables/Medidas.tmdl` | Comparações LY/LM limitadas à janela realizada | A página antiga dependia de um filtro oculto `Passado = TRUE` | Filtro de página | Regra dentro da medida | Funciona em qualquer página |
| `tables/Medidas.tmdl` | Score de recomendação, afinidade, RFV, Pareto/ABC, quadrantes, insights textuais | Novas análises | — | — | Páginas 04, 05 e 06 |
| `tables/Medidas.tmdl` | 50 medidas antigas removidas | Substituídas ou só de formatação do layout antigo | — | — | Ficam no backup |
| `tables/dCalendario.tmdl` | Colunas `Dia`, `DiaUtil`, `Ano Seleção`, `Mês Seleção`, `Mês Ref`; `AnoAtual`/`MesAtual` ocultas; `NomeDia` ordenada por `DiaSemana` | "Atual" passa a depender dos dados, não do relógio | `Date.IsInCurrentYear` no M | DAX ancorado na última venda | Slicers continuam corretos depois de uma atualização |
| `tables/dCliente.tmdl` | 6 colunas calculadas de RFV | Segmentação de clientes | — | `Segmento RFV` etc. | Página Clientes |
| `tables/dClienteSimilar.tmdl` | Recebe as novas colunas de `dCliente` | É cópia calculada de `dCliente` | — | — | Nenhum |
| `tables/pForecast.tmdl`, `pRanking.tmdl`, `pSegmento.tmdl`, `pMétrica.tmdl`, `pDimensão.tmdl`, `dProdutoBase.tmdl` | Novas tabelas | Parâmetros, field parameters, produto âncora | — | — | Interatividade sem bookmarks |
| `tables/auxUX.tmdl` | Removida | Só servia às medidas de cor antigas | — | — | — |
| `relationships.tmdl` | Novo `dCliente[Segmento RFV]` → `pSegmento[Segmento]` | Ordenar e descrever segmentos | 10 relacionamentos | 11 | — |
| `tables/fVendas.tmdl`, `fMetas.tmdl` | Colunas-chave e numéricas brutas ocultas | Evitar agregação implícita | Visíveis | Ocultas | Lista de campos mais limpa |
| `model.tmdl` | Referências às tabelas novas e remoção de `auxUX` | Consequência | — | — | — |

Power Query: nenhuma consulta alterada (ver seção 10 da documentação).

## Relatório

| Arquivo | Alteração | Motivo | Antes | Depois |
|---------|-----------|--------|-------|--------|
| `definition/pages/*` | 5 páginas antigas removidas, 9 novas | Nova arquitetura | Realizado Vs. Meta, Forecast, Recomendações, 2 tooltips | 6 páginas de análise + 3 tooltips |
| `definition/pages/pages.json` | Nova ordem | — | — | — |
| `definition/bookmarks/*` | Removidos (6 bookmarks, 2 grupos) | Trocados por parâmetros desconectados | Abas por bookmark | Slicers `pRanking` e `pForecast` |
| `definition/report.json` | Tema novo; visuais customizados e imagens de fundo removidos; filtro de relatório por dia da semana removido | Só visuais nativos | 12 custom visuals declarados, 5 SVGs | Nenhum custom visual |
| `StaticResources/RegisteredResources/CommercialAnalyticsDark.json` | Novo tema | Design system central | `IPCR - Comercial` + fundos em SVG | Tema único |
| `StaticResources/RegisteredResources/*.svg`, `IPCR_-_Comercial*.json` | Removidos | Layout antigo | — | — |

## Arquivos novos na raiz

`DOCUMENTACAO_REDESIGN.md`, `CHANGELOG_REDESIGN.md`, `_build/` (gerador), `_backup_2026-10-07_original/`.
