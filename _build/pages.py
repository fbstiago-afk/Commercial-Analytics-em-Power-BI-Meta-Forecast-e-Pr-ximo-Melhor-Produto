# -*- coding: utf-8 -*-
"""Definicao das paginas. Cada funcao responde a uma pergunta do storytelling."""
from pbir import *
from components import *
import tokens as T

Y1 = 108            # topo da faixa de KPIs
KPI_H = 96
Y2 = Y1 + KPI_H + T.GAP   # 220


def executiva(root):
    p = Page(root, "p01executiva", "Visão Executiva")
    rail(p, p.name)
    header(p, "Performance Comercial", "O negócio está performando bem?")
    period_slicers(p)
    kpi_strip(p, "kpi", Y1, [
        ("Faturamento", "Faturamento", "Rótulo YoY", "Cor YoY"),
        ("Meta até hoje", "Meta até Hoje", "Rótulo Meta até Hoje", None),
        ("Atingimento", "Atingimento %", "Rótulo Atingimento", "Cor Atingimento"),
        ("Gap para a meta", "Gap Meta", "Rótulo Gap Meta", "Cor Gap Meta"),
        ("Forecast de fechamento", "Forecast", "Rótulo Forecast", "Cor Forecast"),
        ("Ticket médio", "Ticket Médio", "Rótulo Ticket YoY", "Cor Ticket YoY"),
        ("Notas fiscais", "Pedidos", "Rótulo Pedidos YoY", "Cor Pedidos YoY"),
    ])
    hw = 800
    hero = with_vco(line_cumulative(), title="Onde estamos, onde deveríamos estar e para onde vamos",
                    subtitle="Faturamento acumulado no período · realizado, meta e forecast",
                    alt="Linhas acumuladas de realizado, meta e forecast no período, com marcador na última venda.")
    p.add("hero", T.X0, Y2, hw, 330, hero)
    sx = T.X0 + hw + T.GAP
    sw = T.CW - hw - T.GAP
    status = values_on_rows([("Meta", "Meta do período"), ("Faturamento", "Realizado"), ("Forecast", "Forecast"),
                             ("Forecast x Meta", "Gap previsto"), ("Atingimento Forecast %", "Atingimento previsto"),
                             ("Meta Diária Necessária", "Meta diária necessária"),
                             ("Dias Úteis Restantes", "Dias úteis restantes")], size=11,
                            colors={"Forecast x Meta": "Cor Forecast", "Atingimento Forecast %": "Cor Forecast"})
    p.add("status", sx, Y2, sw, 330, with_vco(status, title="Status da meta",
                                               alt="Resumo: meta, realizado, forecast, gap previsto e meta diária necessária."))
    y3 = Y2 + 330 + T.GAP
    h3 = T.H - y3 - T.MARGIN
    panel(p, "ins_bg", T.X0, y3, hw, h3)
    p.add("ins_t", T.X0 + 16, y3 + 12, 300, 22, textbox([[("Leitura executiva", 15, T.TEXT, True)]]))
    p.add("insights", T.X0 + 10, y3 + 38, hw - 20, h3 - 46, text_measure("Leitura Executiva", size=10, col=T.TEXT, width=hw - 44))
    var = variance_month()
    p.add("mensal", sx, y3, sw, h3, with_vco(var, title="Realizado × meta por mês",
                                             subtitle="Barra = faturamento · traço = meta",
                                             alt="Colunas de faturamento mensal coloridas pelo desvio, com a meta como marcador."))
    return p


def variance_month():
    """Variance bar: coluna de faturamento colorida pelo desvio e meta como marcador (barra de erro)."""
    f = "Faturamento"
    return chart("clusteredColumnChart", ("dCalendario", "MesAbre"), [(f, "Faturamento")],
                 tooltips=[("Meta até Hoje", "Meta"), ("Gap Meta", "Gap"), ("Atingimento %", "Atingimento"),
                           ("YoY %", "vs ano anterior"), ("MoM %", "vs mês anterior")],
                 sort=sort_c("dCalendario", "MesNum"),
                 objects={
                     "valueAxis": [props(show=lit(False), gridlineShow=lit(False))],
                     "legend": [props(show=lit(False))],
                     "dataPoint": [props(WILD, fill=color_fx("Cor Gap Meta"))],
                     "labels": [props(show=lit(False))],
                     "error": [
                         props(sel_m(f), enabled=lit(True)),
                         props({"data": [{"dataViewWildcard": {"matchingOption": 0}}], "metadata": mref(f), "highlightMatching": 1},
                               errorRange={"kind": "ErrorRange", "explicit": {"isRelative": lit(False),
                                                                             "upperBound": {"expr": mexpr("Meta até Hoje")}}}),
                         props(sel_m(f), enabled=lit(True), markerShape=lit("longDash"), markerSize=D(6),
                               barColor=color(T.TEXT), barMatchSeriesColor=lit(False), barShow=lit(True),
                               barBorderSize=lit(0), barWidth=lit(1), barBorderColor=color(T.TEXT), labelShow=lit(False)),
                     ]})


def spark(measure, entity, column, display):
    return {"field": {"SparklineData": {"Measure": mexpr(measure), "Groupings": [cexpr(entity, column)]}},
            "queryRef": f"SparklineData({mref(measure)}_[{entity}.{column}])", "nativeQueryRef": display,
            "displayName": display}


def fp_slicer(table, col, value_label, field_ref):
    """Slicer de field parameter com selecao inicial (mesma estrutura gravada pelo Desktop)."""
    fields = col + " Fields"
    litv = {"Literal": {"Value": "'" + field_ref.replace("'", "''") + "'"}}
    flt = {"Version": 2, "From": [{"Name": "p", "Entity": table, "Type": 0}],
           "Where": [{"Condition": {"In": {
               "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "p"}}, "Property": fields}}],
               "Values": [[litv]]}},
               "Annotations": {"filterExpressionMetadata": {
                   "expressions": [cexpr(table, col)],
                   "decomposedIdentities": {"values": [[{"0": [litv]}]], "columns": [{"value": cexpr(table, fields)}]},
                   "valueMap": [{"0": value_label}]}}}]}
    return {"visualType": "slicer",
            "query": {"queryState": {"Values": {"projections": [cproj(table, col)]}}},
            "objects": {"data": [props(mode=lit("Dropdown"))], "header": [props(show=lit(False))],
                        "general": [props(filter={"filter": flt})],
                        "selection": [props(strictSingleSelect=lit(True))]},
            "visualContainerObjects": dict(vco(bg=False, border=False), general=[props(altText=lit("Escolher dimensão de análise"))])}


def performance(root):
    p = Page(root, "p02performance", "Performance")
    rail(p, p.name)
    header(p, "Diagnóstico de Performance", "Por que o resultado aconteceu?")
    period_slicers(p)
    kpi_strip(p, "kpi", Y1, [
        ("Faturamento", "Faturamento", "Rótulo YoY", "Cor YoY"),
        ("Mesmo período do ano anterior", "Faturamento LY", "Rótulo LY", "Cor YoY"),
        ("Itens vendidos", "Quantidade", "Rótulo Quantidade YoY", "Cor Quantidade YoY"),
        ("Atingimento da meta", "Atingimento %", "Rótulo Gap Meta", "Cor Gap Meta"),
        ("Vendedores acima da meta", "Vendedores Acima da Meta", "Rótulo Vendedores", None),
        ("Clientes ativos", "Clientes", "Rótulo Clientes YoY", "Cor Clientes YoY"),
    ])
    h2 = 206
    lw = 700
    p.add("variance", T.X0, Y2, lw, h2, with_vco(variance_month(), title="Em quais meses ficamos acima ou abaixo da meta",
          subtitle="Coluna = faturamento (verde acima, coral abaixo da meta) · traço branco = meta do mês",
          alt="Colunas de faturamento por mês coloridas pelo desvio contra a meta; a meta aparece como traço."))
    rx = T.X0 + lw + T.GAP
    rw = T.CW - lw - T.GAP
    contrib = chart("clusteredBarChart", ("dProduto", "categoria_descricao"), [("Contribuição Crescimento pp", "Contribuição (pp)")],
                    tooltips=[("Faturamento", "Faturamento"), ("Faturamento LY", "Ano anterior"), ("YoY %", "Variação")],
                    sort=sort_m("Contribuição Crescimento pp"), field_param=("pDimensão", "Dimensão"),
                    objects={"dataPoint": [props(WILD, fill=color_fx("Cor YoY"))],
                             "labels": [props(show=lit(True))], "legend": [props(show=lit(False))],
                             "categoryAxis": [props(concatenateLabels=lit(True))]})
    p.add("contrib", rx, Y2, rw, h2, with_vco(contrib, title="Quem puxou o crescimento vs ano anterior",
          subtitle="Pontos percentuais do YoY total · escolha a dimensão ao lado",
          alt="Barras com a contribuição de cada item, em pontos percentuais, para o crescimento contra o ano anterior."))
    p.add("s_dim", rx + rw - 164, Y2 + 8, 150, 30, fp_slicer("pDimensão", "Dimensão", "Categoria", "'dProduto'[categoria_descricao]"))
    y3 = Y2 + h2 + T.GAP
    h3 = T.H - y3 - T.MARGIN
    F = "Faturamento"
    cols = [mproj("Rank Vendedor", "#"), cproj("dVendedor", "descricao", "Vendedor", active=False),
            cproj("dVendedor", "gerente_descricao", "Gerente", active=False), mproj(F, "Faturamento"),
            mproj("Meta até Hoje", "Meta"), mproj("Atingimento %", "Atingimento"),
            mproj("Gap Meta", "Gap"), mproj("YoY %", "vs ano ant."), spark(F, "dCalendario", "MesAbre", "Tendência mensal"),
            mproj("Status Meta", "Status")]
    rank = table(cols, sort=sort_m("Rank Vendedor", desc=False), objects={
        "values": [props(fontSize=D(9)), font_fx("Gap Meta", "Cor Gap Meta"), font_fx("YoY %", "Cor YoY"),
                   font_fx("Status Meta", "Cor Atingimento")],
        "grid": [props(rowPadding=D(2))],
        "columnFormatting": [databar(F), databar("Atingimento %", pos=T.PURPLE2),
                             props(sel_m("Rank Vendedor"), alignment=lit("Center"))],
        "sparklines": [props({"metadata": f"SparklineData({mref(F)}_[dCalendario.MesAbre])"}, chartType=lit("line"),
                             strokeWidth=lit(2), dataColor=color(T.PURPLE2), markers=D(160), markerColor=color(T.CYAN),
                             markerSize=lit(3))]},
        widths={mref("Rank Vendedor"): 40, "dVendedor.descricao": 170, "dVendedor.gerente_descricao": 150, mref(F): 150,
                mref("Meta até Hoje"): 110, mref("Atingimento %"): 130, mref("Gap Meta"): 120, mref("YoY %"): 100,
                f"SparklineData({mref(F)}_[dCalendario.MesAbre])": 120, mref("Status Meta"): 96})
    rank = with_vco(rank, title="Ranking de vendedores", subtitle="Meta e atingimento acumulados até a última venda · ▲ acima, ▼ abaixo, ● em risco (< 80%)",
                    tooltip="tt_vendedor", alt="Tabela com ranking, faturamento, meta, atingimento, gap, variação anual, tendência e status de cada vendedor.")
    p.add("ranking", T.X0, y3, T.CW, h3, rank, filters=[measure_filter("Filtro Ranking", 1)])
    p.add("s_rank", T.X0 + T.CW - 640, y3 + 8, 626, 34, slicer("pRanking", "Visão", "Recorte do ranking", mode="Tiles"))
    return p


def forecast(root):
    p = Page(root, "p03forecast", "Forecast")
    rail(p, p.name)
    header(p, "Forecast de Fechamento", "O que provavelmente vai acontecer até o fechamento?", w=440)
    ids = period_slicers(p, mes_default="Mês Atual")
    sx0 = T.W - T.MARGIN - 5 * 148 + 8
    ids["met"] = p.add("s_met", sx0, 16, 140, 54, slicer("pForecast", "Método", "Método de forecast", single=False))
    kpi_strip(p, "kpi", Y1, [
        ("Realizado", "Faturamento", "Rótulo Gap Meta", "Cor Gap Meta"),
        ("Meta do período", "Meta", "Rótulo Dias Período", None),
        ("Forecast", "Forecast", "Rótulo Forecast", "Cor Forecast"),
        ("Gap previsto", "Forecast x Meta", "Rótulo Gap Previsto", "Cor Forecast"),
        ("Dias úteis restantes", "Dias Úteis Restantes", "Rótulo Dias Corridos", None),
        ("Meta diária original", "Meta Diária Original", "Rótulo Ritmo Original", None),
        ("Realizado por dia útil", "Realizado Diário Médio", "Rótulo Dias Decorridos", None),
        ("Meta diária necessária", "Meta Diária Necessária", "Rótulo Ritmo", "Cor Ritmo"),
    ])
    h2 = 296
    lw = 760
    hero = with_vco(line_cumulative(), title_m="Insight Forecast", subtitle_m="Descrição Método Forecast",
                    alt="Linhas acumuladas de meta, realizado e forecast; o forecast aparece tracejado depois da última venda.")
    p.add("hero", T.X0, Y2, lw, h2, hero)
    rx = T.X0 + lw + T.GAP
    rw = T.CW - lw - T.GAP
    pace = chart("clusteredBarChart", None, [("Realizado Diário Médio", "Realizado por dia útil"),
                                              ("Meta Diária Original", "Meta diária original"),
                                              ("Meta Diária Necessária", "Meta diária necessária")],
                 objects={"dataPoint": [props(sel_m("Realizado Diário Médio"), fill=color(T.PURPLE)),
                                        props(sel_m("Meta Diária Original"), fill=color(T.MUTED)),
                                        props(sel_m("Meta Diária Necessária"), fill=color(T.AMBER))],
                          "labels": [props(show=lit(True))], "legend": [props(show=lit(True), position=lit("Bottom"))],
                          "categoryAxis": [props(show=lit(False))]})
    p.add("pace", rx, Y2, rw, h2, with_vco(pace, title="O ritmo atual é suficiente para bater a meta?",
          subtitle_m="Insight Ritmo", alt="Três barras: faturamento por dia útil realizado, meta diária original e meta diária necessária."))
    y3 = Y2 + h2 + T.GAP
    h3 = T.H - y3 - T.MARGIN
    w3 = (T.CW - 2 * T.GAP) / 3
    met = chart("clusteredColumnChart", ("pForecast", "Método"), [("Forecast", "Forecast")],
                tooltips=[("Atingimento Forecast %", "Atingimento previsto"), ("Forecast x Meta", "Gap previsto")],
                sort=sort_c("pForecast", "Ordem"),
                objects={"dataPoint": [props(WILD, fill=color_fx("Cor Forecast"))],
                         "labels": [props(show=lit(True), labelPosition=lit("InsideEnd"), color=color(T.BG))],
                         "legend": [props(show=lit(False))], "valueAxis": [props(show=lit(False), gridlineShow=lit(False))],
                         "y1AxisReferenceLine": [props({"id": "1"}, show=lit(True), displayName=lit("Meta"),
                                                       value={"expr": mexpr("Meta")}, lineColor=color(T.TEXT),
                                                       style=lit("dashed"), dataLabelShow=lit(True),
                                                       dataLabelColor=color(T.TEXT2), dataLabelText=lit("Name"))]})
    metn = p.add("methods", T.X0, y3, w3, h3, with_vco(met, title="Quanto os métodos divergem",
          subtitle="Fechamento projetado por método · linha tracejada = meta · backtest: Adaptativo errou 9,7% em média, Plano de Metas 15,0%",
          alt="Colunas com o forecast de fechamento de cada um dos cinco métodos, comparados com a meta."))
    saz = chart("clusteredColumnChart", ("dCalendario", "MesAbre"), [("Índice Sazonal", "Índice sazonal")],
                sort=sort_c("dCalendario", "MesNum"),
                objects={"dataPoint": [props(fill=color(T.PURPLE2))], "labels": [props(show=lit(True))],
                         "legend": [props(show=lit(False))], "valueAxis": [props(show=lit(False), gridlineShow=lit(False))],
                         "y1AxisReferenceLine": [props({"id": "1"}, show=lit(True), displayName=lit("Média"),
                                                       value=D(1), lineColor=color(T.TEXT2), style=lit("dashed"))]})
    sazn = p.add("saz", T.X0 + w3 + T.GAP, y3, w3, h3, with_vco(saz, title="Sazonalidade histórica por mês",
          subtitle="Faturamento médio do mês ÷ média mensal do histórico (1,00 = mês médio)",
          alt="Colunas com o índice sazonal de cada mês do ano, calculado sobre os meses completos do histórico."))
    dow = chart("clusteredBarChart", ("dCalendario", "NomeDia"), [("Índice Dia da Semana", "Índice")],
                sort=sort_c("dCalendario", "DiaSemana"),
                objects={"dataPoint": [props(fill=color(T.CYAN))], "labels": [props(show=lit(True))],
                         "legend": [props(show=lit(False))], "valueAxis": [props(show=lit(False), gridlineShow=lit(False))]})
    down = p.add("dow", T.X0 + 2 * (w3 + T.GAP), y3, w3, h3, with_vco(dow, title="O fim de semana também vende",
          subtitle="Venda média por dia da semana ÷ média diária (12 meses) · por isso o run rate usa dias corridos",
          alt="Colunas com o índice de vendas por dia da semana nos últimos doze meses."))
    for sl in ("ano", "mes"):
        p.no_filter(ids[sl], sazn)
        p.no_filter(ids[sl], down)
    p.no_filter(ids["met"], metn)
    return p


def produtos(root):
    p = Page(root, "p04produtos", "Produtos")
    rail(p, p.name)
    header(p, "Performance de Produtos", "Quais produtos explicam o resultado?")
    period_slicers(p)
    kpi_strip(p, "kpi", Y1, [
        ("Faturamento", "Faturamento", "Rótulo YoY", "Cor YoY"),
        ("Itens vendidos", "Quantidade", "Rótulo Quantidade YoY", "Cor Quantidade YoY"),
        ("Produtos vendidos", "Produtos Vendidos", "Rótulo SKUs", None),
        ("Preço médio por item", "Preço Médio", "Rótulo Itens Pedido", None),
        ("Participação do top 10", "Share Top 10 %", "Rótulo Classe A", None),
        ("Margem bruta", "Margem %", "Rótulo Margem", None),
    ])
    h2 = 270
    lw = 560
    D_ = ("dProduto", "descricao")
    sc = chart("scatterChart", D_, [("Participação %", "Participação")], xs=[("YoY %", "Crescimento vs ano anterior")],
               size=("Quantidade", "Itens"), tooltips=[("Faturamento", "Faturamento"), ("Quadrante Produto", "Quadrante")],
               objects={"dataPoint": [props(WILD, fill=color_fx("Cor Quadrante"))],
                        "categoryLabels": [props(show=lit(True))], "legend": [props(show=lit(False))],
                        "categoryAxis": [props(showAxisTitle=lit(True), titleColor=color(T.TEXT2), titleFontSize=D(9))],
                        "valueAxis": [props(showAxisTitle=lit(True), titleColor=color(T.TEXT2), titleFontSize=D(9))],
                        "xAxisReferenceLine": [props({"id": "1"}, show=lit(True), displayName=lit("Crescimento total"),
                                                     value={"expr": mexpr("YoY Total Produtos %")}, lineColor=color(T.TEXT2),
                                                     style=lit("dashed"), dataLabelShow=lit(True), dataLabelColor=color(T.TEXT2),
                                                     dataLabelText=lit("Name"))],
                        "y1AxisReferenceLine": [props({"id": "1"}, show=lit(True), displayName=lit("Participação média"),
                                                      value={"expr": mexpr("Participação Média %")}, lineColor=color(T.TEXT2),
                                                      style=lit("dashed"), dataLabelShow=lit(True), dataLabelColor=color(T.TEXT2),
                                                      dataLabelText=lit("Name"))]})
    p.add("matrix", T.X0, Y2, lw, h2, with_vco(sc, title="Matriz de performance: quem ganha e quem perde participação",
          subtitle="Verde = estrela · ciano = crescimento · coral = atenção · cinza = baixa relevância · bolha = itens vendidos",
          tooltip="tt_produto", alt="Dispersão de produtos por crescimento anual e participação no faturamento, com quadrantes."))
    rx = T.X0 + lw + T.GAP
    rw = T.CW - lw - T.GAP
    par = chart("lineClusteredColumnComboChart", D_, [("Faturamento", "Faturamento")], y2=[("Pareto %", "Acumulado %")],
                sort=sort_m("Faturamento"),
                objects={"dataPoint": [props(dict(WILD, metadata=mref("Faturamento")), fill=color_fx("Cor ABC")),
                                       props(sel_m("Pareto %"), fill=color(T.CYAN))],
                         "legend": [props(show=lit(False))], "labels": [props(show=lit(False))],
                         "lineStyles": [props(strokeWidth=D(2), showMarker=lit(False))],
                         "valueAxis": [props(show=lit(False), gridlineShow=lit(False), secShow=lit(True), secLabelColor=color(T.TEXT2), secFontSize=D(9),
                                             secShowAxisTitle=lit(False), secStart=D(0), secEnd=D(1))]})
    p.add("pareto", rx, Y2, rw, h2, with_vco(par, title="Pareto: poucos produtos concentram o resultado",
          subtitle_m="Rótulo Classe A", tooltip="tt_produto",
          alt="Colunas de faturamento por produto em ordem decrescente e linha de participação acumulada."))
    y3 = Y2 + h2 + T.GAP
    h3 = T.H - y3 - T.MARGIN
    tw = 760
    cols = [mproj("Rank Produto", "#"), cproj(*D_, "Produto", active=False),
            cproj("dProduto", "categoria_descricao", "Categoria", active=False), mproj("Classe ABC", "ABC"),
            mproj("Faturamento", "Faturamento"), mproj("Participação %", "Part."), mproj("YoY %", "vs ano ant."),
            mproj("Contribuição Crescimento pp", "Contrib."), mproj("Penetração %", "Penetr."),
            mproj("Penetração Δ pp", "Δ penetr."), mproj("Quadrante Produto", "Quadrante")]
    tb = table(cols, sort=sort_m("Faturamento"), objects={
        "values": [props(fontSize=D(9)), font_fx("YoY %", "Cor YoY"), font_fx("Contribuição Crescimento pp", "Cor YoY"),
                   font_fx("Quadrante Produto", "Cor Quadrante"), font_fx("Classe ABC", "Cor ABC")],
        "columnFormatting": [databar("Faturamento"), props(sel_m("Rank Produto"), alignment=lit("Center")),
                             props(sel_m("Classe ABC"), alignment=lit("Center"))]})
    p.add("ptable", T.X0, y3, tw, h3, with_vco(tb, title="Crescimento, queda e penetração por produto",
          subtitle="Ordene pelas colunas para ver top crescimento e top queda · penetração = % dos clientes ativos que compraram",
          tooltip="tt_produto", alt="Tabela de produtos com classe ABC, faturamento, participação, crescimento, contribuição e penetração."))
    ax = T.X0 + tw + T.GAP
    aw = T.CW - tw - T.GAP
    af = chart("clusteredBarChart", D_, [("% Também Compraram", "% também compraram")],
               tooltips=[("Clientes Também Compraram", "Clientes em comum"), ("Lift Afinidade", "Lift")],
               sort=sort_m("% Também Compraram"),
               objects={"dataPoint": [props(fill=color(T.CYAN))], "labels": [props(show=lit(True))],
                        "legend": [props(show=lit(False))]})
    p.add("affinity", ax, y3, aw, h3, with_vco(af, title="Quem comprou também comprou…",
          subtitle_m="Insight Afinidade", alt="Barras com o percentual dos clientes do produto âncora que também compraram cada produto."))
    p.add("s_base", ax + aw - 184, y3 + 10, 170, 28,
          slicer("dProdutoBase", "Produto Base", "Produto âncora", default="Incomparaveis", single=True, show_header=False))
    return p


def clientes(root):
    p = Page(root, "p05clientes", "Clientes")
    rail(p, p.name)
    header(p, "Inteligência de Clientes", "Quais clientes explicam o resultado e onde está o risco?")
    period_slicers(p)
    kpi_strip(p, "kpi", Y1, [
        ("Clientes ativos no período", "Clientes", "Rótulo Clientes YoY", "Cor Clientes YoY"),
        ("Clientes novos", "Clientes Novos", "Rótulo Novos", None),
        ("Sem recompra", "Clientes Sem Recompra", "Rótulo Sem Recompra", None),
        ("Ticket médio", "Ticket Médio", "Rótulo Ticket YoY", "Cor Ticket YoY"),
        ("Concentração", "Share Top 10 Clientes %", "Rótulo Concentração", None),
        ("Clientes em risco", "Clientes em Risco", "Rótulo Risco", None),
        ("Recência média (dias)", "Recência Média (dias)", "Rótulo Carteira", None),
    ])
    h2 = 262
    lw = 840
    seg = table([cproj("pSegmento", "Segmento", "Segmento", active=False), mproj("Clientes na Carteira", "Clientes"),
                 mproj("Carteira %", "% carteira"), mproj("Faturamento 12M", "Fat. 12M"),
                 mproj("Recência Média (dias)", "Recência"),
                 cproj("pSegmento", "Ação sugerida", "Ação sugerida", active=False)],
                sort=sort_c("pSegmento", "Ordem"),
                objects={"values": [props(fontSize=D(9))], "grid": [props(rowPadding=D(4))],
                         "columnFormatting": [databar("Clientes na Carteira"), databar("Faturamento 12M", pos=T.CYAN)]},
                widths={"pSegmento.Segmento": 74, mref("Clientes na Carteira"): 78, mref("Carteira %"): 64,
                        mref("Faturamento 12M"): 100, mref("Recência Média (dias)"): 60, "pSegmento.Ação sugerida": 430})
    p.add("segments", T.X0, Y2, lw, h2, with_vco(seg, title="Segmentos RFV: onde agir primeiro",
          subtitle="Foto dos últimos 12 meses na data da última venda · regras de recência, frequência e valor (não é cluster estatístico)",
          alt="Tabela com os segmentos RFV, número de clientes, faturamento, ticket, recência e ação sugerida."))
    rx = T.X0 + lw + T.GAP
    rw = T.CW - lw - T.GAP
    sc = {"visualType": "scatterChart",
          "query": {"queryState": {"Category": {"projections": [cproj("dCliente", "descricao", "Cliente")]},
                                   "Series": {"projections": [cproj("dCliente", "Segmento RFV", "Segmento")]},
                                   "X": {"projections": [mproj("Recência Média (dias)", "Dias desde a última compra")]},
                                   "Y": {"projections": [mproj("Faturamento 12M", "Faturamento 12M")]},
                                   "Size": {"projections": [mproj("Pedidos 12M", "Notas 12M")]}}},
          "objects": {"legend": [props(show=lit(True), position=lit("Top"))],
                      "dataPoint": [props({"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0,
                                           "Left": cexpr("dCliente", "Segmento RFV"),
                                           "Right": {"Literal": {"Value": "'" + sname + "'"}}}}}]}, fill=color(scol))
                                    for sname, scol in (("VIP", T.PURPLE), ("Leais", T.PURPLE2), ("Potencial", T.CYAN),
                                                        ("Novos", T.GREEN), ("Em risco", T.AMBER), ("Inativos", T.MUTED))],
                      "categoryAxis": [props(showAxisTitle=lit(True), titleColor=color(T.TEXT2), titleFontSize=D(9))],
                      "valueAxis": [props(showAxisTitle=lit(False))]}}
    p.add("rfm", rx, Y2, rw, h2, with_vco(sc, title="Recência × valor: quem está esfriando",
          subtitle="Cada ponto é um cliente · à direita = mais tempo sem comprar",
          tooltip="tt_cliente", alt="Dispersão de clientes por dias desde a última compra e faturamento em doze meses, por segmento."))
    y3 = Y2 + h2 + T.GAP
    h3 = T.H - y3 - T.MARGIN
    tw = 800
    cl = table([cproj("dCliente", "descricao", "Cliente", active=False), cproj("dCliente", "Segmento RFV", "Segmento", active=False),
                cproj("dCliente", "uf", "UF", active=False), mproj("Faturamento", "Faturamento"), mproj("YoY %", "vs ano ant."),
                mproj("Pedidos", "Notas"), mproj("Ticket Médio", "Ticket"), mproj("SKUs Vendidos", "Mix (SKUs)"),
                mproj("Última Compra Cliente", "Última compra"), mproj("Recência Média (dias)", "Recência")],
               sort=sort_m("Faturamento"),
               objects={"values": [props(fontSize=D(9)), font_fx("YoY %", "Cor YoY")],
                        "columnFormatting": [databar("Faturamento")]})
    p.add("ctable", T.X0, y3, tw, h3, with_vco(cl, title="Clientes do período",
          subtitle="Faturamento, crescimento, ticket, mix e recência · passe o mouse para o perfil completo",
          tooltip="tt_cliente", alt="Tabela de clientes com faturamento, variação anual, notas, ticket, mix, última compra e recência."))
    bx = T.X0 + tw + T.GAP
    bw = T.CW - tw - T.GAP
    bar = chart("clusteredBarChart", ("pSegmento", "Segmento"), [("Faturamento", "Faturamento")],
                tooltips=[("Clientes", "Clientes ativos"), ("YoY %", "vs ano anterior")], sort=sort_c("pSegmento", "Ordem"),
                objects={"dataPoint": [props(fill=color(T.PURPLE))], "labels": [props(show=lit(True))],
                         "legend": [props(show=lit(False))]})
    p.add("segbar", bx, y3, bw, h3, with_vco(bar, title="Faturamento do período por segmento",
          subtitle_m="Insight Clientes", alt="Barras com o faturamento do período por segmento RFV."))
    return p


def nbp(root):
    p = Page(root, "p06nbp", "Next Best Product")
    rail(p, p.name)
    header(p, "Next Best Product", "O que o comercial deve oferecer a este cliente agora?", subtitle_m="Subtítulo Cliente", w=640)
    x = T.W - T.MARGIN - (250 + 2 * 148) + 8
    p.add("s_cli", x, 16, 242, 54, slicer("dCliente", "descricao", "Cliente", default="Bailey Inc", single=True, search=True))
    p.add("s_ano", x + 250, 16, 140, 54, slicer("dCalendario", "Ano Seleção", "Ano", "Ano Atual", single=True))
    p.add("s_mes", x + 398, 16, 140, 54, slicer("dCalendario", "Mês Seleção", "Mês"))
    kpi_strip(p, "kpi", Y1, [
        ("Faturamento 12 meses", "Faturamento 12M", "Rótulo Segmento", None),
        ("Notas em 12 meses", "Pedidos 12M", "Rótulo Ticket 12M", None),
        ("Mix em 12 meses", "SKUs 12M", "Rótulo Mix", None),
        ("Última compra", "Última Compra Cliente", "Rótulo Recência", None),
        ("Clientes similares", "Clientes Similares", "Rótulo Similaridade", None),
        ("Produtos recomendados", "Produtos Recomendados", "Rótulo Recomendados", None),
    ])
    y3h = 104
    h2 = T.H - Y2 - T.MARGIN - y3h - T.GAP
    w1, w2 = 404, 356
    w3 = T.CW - w1 - w2 - 2 * T.GAP
    hist = table([cproj("dProduto", "descricao", "Produto", active=False), cproj("dProduto", "tamanho", "Tam.", active=False),
                  mproj("Qtd Histórica", "Qtd"), mproj("Compras do Produto", "Vezes"),
                  mproj("Última Compra Produto", "Última"), mproj("Qtd Recompra Sugerida", "Recompra")],
                 sort=sort_m("Qtd Histórica"),
                 objects={"values": [props(fontSize=D(9), wordWrap=lit(False))],
                          "columnFormatting": [databar("Qtd Histórica"), databar("Qtd Recompra Sugerida", pos=T.AMBER)]},
                 widths={"dProduto.descricao": 104, "dProduto.tamanho": 32, mref("Qtd Histórica"): 42,
                         mref("Compras do Produto"): 42, mref("Última Compra Produto"): 82, mref("Qtd Recompra Sugerida"): 54})
    p.add("hist", T.X0, Y2, w1, h2, with_vco(hist, title="1 · Histórico do cliente",
          subtitle="Todo o histórico · 'Vezes' = notas em que o item apareceu · 'Recompra' = itens sem compra no período",
          alt="Tabela com os produtos já comprados pelo cliente, quantidade, recorrência, última compra e sugestão de recompra."),
          filters=[measure_filter("Qtd Histórica", 0, kind=1)])
    x2 = T.X0 + w1 + T.GAP
    hs = 212
    sim = table([cproj("dClienteSimilar", "descricao", "Cliente similar", active=False), mproj("Similaridade", "Similaridade"),
                 mproj("Faturamento Similar 12M", "Fat. 12M"), mproj("SKUs Similar 12M", "Mix")],
                sort=sort_m("Similaridade"),
                objects={"values": [props(fontSize=D(10))], "grid": [props(rowPadding=D(4))],
                         "columnFormatting": [databar("Similaridade", pos=T.CYAN)]},
                widths={"dClienteSimilar.descricao": 132, mref("Similaridade"): 78, mref("Faturamento Similar 12M"): 74,
                        mref("SKUs Similar 12M"): 40})
    p.add("similar", x2, Y2, w2, hs, with_vco(sim, title="2 · Clientes com mix parecido",
          subtitle="Similaridade de cosseno do mix de compras (índice de 0 a 100%, não é probabilidade)",
          alt="Tabela com até três clientes similares, similaridade, faturamento e mix."),
          filters=[measure_filter("Similaridade", 0, kind=1)])
    prof = values_on_rows([("Segmento Cliente", "Segmento RFV"), ("Cidade Cliente", "Cidade"),
                           ("Primeira Compra Cliente", "Cliente desde"), ("Recência Cliente (dias)", "Recência"),
                           ("Ticket Médio 12M", "Ticket médio 12M")], size=10)
    p.add("profile", x2, Y2 + hs + T.GAP, w2, h2 - hs - T.GAP, with_vco(prof, title="Perfil do cliente",
          alt="Segmento, cidade, data da primeira compra, recência e ticket do cliente."))
    x3 = x2 + w2 + T.GAP
    nb = table([mproj("Rank NBP", "#"), cproj("dProduto", "descricao", "Produto", active=False),
                cproj("dProduto", "tamanho", "Tam.", active=False), mproj("Score Recomendação", "Score"),
                mproj("Similares que Compraram", "Similares"), mproj("Oportunidade NBP", "Oportunidade")],
               sort=sort_m("Rank NBP", desc=False),
               objects={"values": [props(fontSize=D(10)), font_fx("Oportunidade NBP", "Cor Score")],
                        "grid": [props(rowPadding=D(5))],
                        "columnFormatting": [databar("Score Recomendação", pos=T.GREEN),
                                             props(sel_m("Rank NBP"), alignment=lit("Center"))]})
    p.add("nbp", x3, Y2, w3, h2, with_vco(nb, title="3 · Next best products",
          subtitle="Produtos que os similares compram e este cliente ainda não comprou no período · score heurístico de 0 a 100",
          tooltip="tt_produto", alt="Ranking de produtos recomendados com score, quantos similares compraram e nível de oportunidade."),
          filters=[measure_filter("Score Recomendação", 0, kind=1)])
    ya = Y2 + h2 + T.GAP
    panel(p, "action_bg", T.X0, ya, T.CW, y3h)
    p.add("action_t", T.X0 + 16, ya + 12, 400, 22, textbox([[("4 · Ação comercial sugerida", 14, T.TEXT, True)]]))
    p.add("action", T.X0 + 12, ya + 38, T.CW - 24, y3h - 46, text_measure("Insight NBP", size=12, col=T.TEXT))
    return p


def tooltip_page(root, name, display, title, rows, trend=True):
    p = Page(root, name, display, width=320, height=280 if trend else 214, tooltip=True)
    p.add("t", 14, 10, 292, 20, textbox([[(title, 11, T.TEXT2, True)]]))
    v = values_on_rows(rows, size=9)
    v["visualContainerObjects"] = dict(vco(bg=False, border=False), padding=[props(top=D(0), bottom=D(0), left=D(0), right=D(0))])
    v["objects"]["values"][0]["properties"].update(backColorPrimary=color(T.ELEVATED), backColorSecondary=color(T.ELEVATED))
    v["objects"]["rowHeaders"][0]["properties"].update(backColor=color(T.ELEVATED))
    v["objects"]["columnHeaders"][0]["properties"].update(backColor=color(T.ELEVATED), fontColor=color(T.ELEVATED))
    v["objects"]["grid"] = [props(gridHorizontal=lit(False), gridVertical=lit(False), rowPadding=D(2))]
    p.add("list", 10, 32, 300, 168, v)
    if trend:
        tr = chart("clusteredColumnChart", ("dCalendario", "MesAbre"), [("Faturamento", "Faturamento")],
                   sort=sort_c("dCalendario", "MesNum"),
                   objects={"dataPoint": [props(fill=color(T.PURPLE))], "legend": [props(show=lit(False))],
                            "valueAxis": [props(show=lit(False), gridlineShow=lit(False))],
                            "categoryAxis": [props(fontSize=D(8))], "labels": [props(show=lit(False))]})
        tr["visualContainerObjects"] = dict(vco(bg=False, border=False), padding=[props(top=D(0), bottom=D(0), left=D(0), right=D(0))])
        p.add("trend", 10, 200, 300, 72, tr)
    return p


def build_all(root):
    return [executiva(root), performance(root), forecast(root), produtos(root), clientes(root), nbp(root),
            tooltip_page(root, "tt_produto", "Tooltip Produto", "PRODUTO",
                         [("Faturamento", "Faturamento"), ("Quantidade", "Itens"), ("Participação %", "Participação"),
                          ("YoY %", "vs ano anterior"), ("Preço Médio", "Preço médio"), ("Penetração %", "Penetração"),
                          ("Última Compra Produto", "Última venda")]),
            tooltip_page(root, "tt_vendedor", "Tooltip Vendedor", "VENDEDOR",
                         [("Faturamento", "Faturamento"), ("Meta até Hoje", "Meta até hoje"), ("Atingimento %", "Atingimento"),
                          ("Gap Meta", "Gap"), ("Status Meta", "Status"), ("YoY %", "vs ano anterior"),
                          ("Forecast", "Forecast do período")]),
            tooltip_page(root, "tt_cliente", "Tooltip Cliente", "CLIENTE",
                         [("Faturamento 12M", "Faturamento 12M"), ("Pedidos 12M", "Notas 12M"), ("Ticket Médio 12M", "Ticket 12M"),
                          ("SKUs 12M", "Mix (SKUs)"), ("Última Compra Cliente", "Última compra"),
                          ("Recência Média (dias)", "Recência (dias)")], trend=False)]
