# Commercial Analytics em Power BI: Meta, Forecast e Próximo Melhor Produto

<!-- portfolio-link:start -->
[![Ver no portfólio](https://img.shields.io/badge/Ver%20o%20painel%20no%20portf%C3%B3lio-Bocardi%20Data-6C3BAA?style=for-the-badge)](https://bocardidata.base44.app/ProjectDetail?id=commercial-analytics-meta-forecast)

> 🔗 **Quer ver o visual do Power BI?** Acesse a página do projeto no portfólio: **[https://bocardidata.base44.app/ProjectDetail?id=commercial-analytics-meta-forecast](https://bocardidata.base44.app/ProjectDetail?id=commercial-analytics-meta-forecast)**
<!-- portfolio-link:end -->


Solução executiva de analytics comercial em Power BI (PBIP/TMDL) que responde: estamos acima ou abaixo da meta? o que acontecerá até o fechamento? quais vendedores, produtos e clientes explicam o resultado? qual ação comercial tomar?

## Páginas
1. Visão Executiva
2. Performance Comercial
3. Forecast (5 métodos, backtest de 19 meses: MAPE 9,7% adaptativo vs 15,0% plano de metas)
4. Produtos (matriz, Pareto/ABC, afinidade)
5. Clientes (segmentação RFV)
6. Recomendação / Next Best Product (clientes similares + score heurístico 0–100, não é probabilidade)

## Destaques técnicos
- Esquema estrela (fVendas, fMetas, dCalendario, dCliente, dProduto, dVendedor)
- 174 medidas DAX organizadas em Display Folders
- Field parameters, calculation group, dynamic format strings, títulos e insights dinâmicos, tooltips
- Tema Dark Premium centralizado em JSON
- Gerador do relatório em Python (`_build/`)

## Estrutura
- `Dashboard Comercial.pbip`: abrir no Power BI Desktop (modo de projeto)
- `Dashboard Comercial.SemanticModel/`: modelo em TMDL
- `Dashboard Comercial.Report/`: relatório em PBIR
- `DOCUMENTACAO_REDESIGN.md` e `CHANGELOG_REDESIGN.md`: documentação completa e validação antes × depois

## Observações
- Os dados de origem (Excel/CSV de treinamento) não estão no repositório; ajuste os caminhos no Power Query para a sua cópia.
- Base de treinamento com dados sintéticos; o método é aplicável a dados reais.
