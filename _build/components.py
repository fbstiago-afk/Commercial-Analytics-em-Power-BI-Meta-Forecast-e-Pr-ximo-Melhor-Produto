# -*- coding: utf-8 -*-
"""Componentes reutilizaveis do relatorio (rail, cabecalho, slicers, KPIs, graficos, tabelas)."""
from pbir import *
import tokens as T

NAV = [
    ("p01executiva", "Visão Executiva", "01", "O negócio está performando bem?"),
    ("p02performance", "Performance", "02", "Por que o resultado aconteceu?"),
    ("p03forecast", "Forecast", "03", "Como o período deve fechar?"),
    ("p04produtos", "Produtos", "04", "Quais produtos explicam o resultado?"),
    ("p05clientes", "Clientes", "05", "Quais clientes explicam o resultado?"),
    ("p06nbp", "Recomendação", "06", "Next Best Product: o que o comercial deve fazer agora?"),
]


def shape(bg, radius=0):
    return {"visualType": "shape",
            "objects": {"fill": [props(show=lit(False))], "outline": [props(show=lit(False))]},
            "visualContainerObjects": dict(vco(bg=True, bg_color=bg, border=bg, radius=radius),
                                           padding=[props(top=D(0), bottom=D(0), left=D(0), right=D(0))])}


def textbox(runs, align="left"):
    """runs: lista de paragrafos; cada paragrafo e lista de (texto, tamanho_px, cor, negrito)."""
    paras = []
    for para in runs:
        tr = []
        for text, size, col, bold in para:
            st = {"fontFamily": T.FONT, "fontSize": f"{size}px", "color": col}
            if bold:
                st["fontWeight"] = "bold"
            tr.append({"value": text, "textStyle": st})
        p = {"textRuns": tr}
        if align != "left":
            p["horizontalTextAlignment"] = align
        paras.append(p)
    return {"visualType": "textbox", "objects": {"general": [props(paragraphs=paras)]},
            "visualContainerObjects": vco(bg=False, border=False)}


def nav_button(label, target, active, tip):
    fg = T.TEXT if active else T.TEXT2
    fill = [props(show=lit(True)),
            props({"id": "default"}, show=lit(True), fillColor=color(T.PURPLE if active else T.BG2), transparency=D(0)),
            props({"id": "hover"}, show=lit(True), fillColor=color(T.PURPLE if active else T.SURFACE), transparency=D(0))]
    text = [props(show=lit(True)),
            props({"id": "default"}, show=lit(True), text=lit(label), fontColor=color(fg), fontSize=D(10),
                  fontFamily=lit(T.FONT_SB if active else T.FONT), horizontalAlignment=lit("left"),
                  leftMargin=D(12), bold=lit(False)),
            props({"id": "hover"}, show=lit(True), text=lit(label), fontColor=color(T.TEXT), fontSize=D(10),
                  fontFamily=lit(T.FONT_SB if active else T.FONT), horizontalAlignment=lit("left"), leftMargin=D(12))]
    v = {"visualType": "actionButton",
         "objects": {"icon": [props(show=lit(False))], "outline": [props(show=lit(False))],
                     "fill": fill, "text": text,
                     "shape": [props({"id": "default"}, tileShape=lit("rectangleRounded"), rectangleRoundedCurve=lit(18))]},
         "visualContainerObjects": {"visualLink": [props(show=lit(True), type=lit("PageNavigation"),
                                                         navigationSection=lit(target), tooltip=lit(tip))],
                                    "background": [props(show=lit(False))], "border": [props(show=lit(False))],
                                    "title": [props(show=lit(False))],
                                    "general": [props(altText=lit(tip))]}}
    return v


def rail(page, active):
    page.add("rail", 0, 0, T.RAIL, T.H, shape(T.BG2))
    page.add("brand", 20, 26, 136, 52, textbox([[("COMMERCIAL", 13, T.TEXT, True)], [("ANALYTICS", 11, T.PURPLE2, True)]]))
    page.add("raildiv", 20, 92, 128, 1, shape(T.DIVIDER))
    y = 112
    for name, label, num, question in NAV:
        page.add("nav_" + name, 12, y, 144, 38,
                 nav_button(f"{num}   {label}", name, name == active, f"{label}: {question}"))
        y += 44
    page.add("railfoot", 20, T.H - 78, 136, 56,
             textbox([[("Realizado · Meta", 9, T.MUTED, False)], [("Forecast · Clientes · NBP", 9, T.MUTED, False)]]))


def text_measure(measure, size=9, col=None, color_m=None, bold=False, align="Left", width=None):
    """Texto dinamico (medida) alinhado a esquerda e com quebra de linha: tabela de 1 coluna sem cabecalho."""
    vals = {"fontSize": D(size), "wordWrap": lit(True)}
    if col:
        vals["fontColorPrimary"] = color(col)
        vals["fontColorSecondary"] = color(col)
    if color_m:
        vals["fontColorPrimary"] = color_fx(color_m)
        vals["fontColorSecondary"] = color_fx(color_m)
    if bold:
        vals["bold"] = lit(True)
    cw = [props(sel_m(measure), value=D(width))] if width else []
    return {"visualType": "tableEx",
            "query": {"queryState": {"Values": {"projections": [mproj(measure, " ")]}}},
            "objects": {"values": [props(**vals)], "columnWidth": cw,
                        "columnHeaders": [props(fontSize=D(1), fontColor=color(T.BG), backColor=color(T.BG),
                                                outlineStyle=D(0), autoSizeColumnWidth=lit(not width))],
                        "grid": [props(gridHorizontal=lit(False), gridVertical=lit(False), rowPadding=D(0),
                                       outlineWeight=D(0))],
                        "total": [props(totals=lit(False))],
                        "columnFormatting": [props(sel_m(measure), alignment=lit(align))]},
            "visualContainerObjects": dict(vco(bg=False, border=False), padding=[props(top=D(0), bottom=D(0), left=D(0), right=D(0))])}


def header(page, title, question, subtitle_m="Subtítulo Contexto", w=600):
    page.add("h_title", T.X0, 16, w, 34, textbox([[(title, 22, T.TEXT, True)]]))
    page.add("h_question", T.X0, 50, w, 20, textbox([[(question, 11, T.PURPLE2, False)]]))
    v = text_measure(subtitle_m, size=9, col=T.TEXT2)
    v["objects"]["values"][0]["properties"]["backColorPrimary"] = color(T.BG)
    v["objects"]["values"][0]["properties"]["backColorSecondary"] = color(T.BG)
    page.add("h_sub", T.X0 - 4, 70, w + 40, 30, v)


def slicer(entity, column, label, default=None, single=False, sync=None, mode="Dropdown", search=False, show_header=True):
    general = {}
    if default:
        general["filter"] = slicer_filter(entity, column, default)
    if search:
        general["selfFilterEnabled"] = lit(True)
    if mode == "Tiles":
        general["orientation"] = D(1)
    o = {"data": [props(mode=lit("Basic" if mode == "Tiles" else mode))],
         "header": [props(show=lit(mode != "Tiles" and show_header), text=lit(label))]}
    if general:
        o["general"] = [props(**general)]
    if single:
        o["selection"] = [props(strictSingleSelect=lit(True))]
    elif mode == "Tiles":
        o["selection"] = [props(singleSelect=lit(True))]
    v = {"visualType": "slicer",
         "query": {"queryState": {"Values": {"projections": [cproj(entity, column, label)]}}},
         "objects": o,
         "visualContainerObjects": dict(vco(bg=False, border=False), general=[props(altText=lit("Filtro: " + label))])}
    if sync:
        v["syncGroup"] = {"groupName": sync, "fieldChanges": True, "filterChanges": True}
    return v


def period_slicers(page, mes_default=None, extra=True):
    """Barra compacta superior: Ano, Mes, Gerente, Categoria."""
    x = T.W - T.MARGIN - 4 * 148 + 8
    ids = {}
    ids["ano"] = page.add("s_ano", x, 16, 140, 54, slicer("dCalendario", "Ano Seleção", "Ano", "Ano Atual", single=True, sync="Ano"))
    ids["mes"] = page.add("s_mes", x + 148, 16, 140, 54, slicer("dCalendario", "Mês Seleção", "Mês", mes_default))
    if extra:
        ids["ger"] = page.add("s_ger", x + 296, 16, 140, 54, slicer("dVendedor", "gerente_descricao", "Gerente", sync="Gerente"))
        ids["cat"] = page.add("s_cat", x + 444, 16, 140, 54, slicer("dProduto", "categoria_descricao", "Categoria", sync="Categoria"))
    return ids


def panel(page, key, x, y, w, h):
    return page.add(key, x, y, w, h, shape(T.BG2, T.RADIUS))


def kpi_strip(page, key, y, items, x=None, w=None, h=96):
    """Linha executiva de KPIs. items: (rotulo, medida_valor, medida_comparacao|None, medida_cor|None).
    Duas tabelas de 1 linha (valores e comparacoes) = 2 consultas para a faixa inteira."""
    x = T.X0 if x is None else x
    w = T.CW if w is None else w
    panel(page, key + "_bg", x, y, w, h)
    n = len(items)
    cw = (w - 24) / n
    nogrid = [props(gridHorizontal=lit(False), gridVertical=lit(False), rowPadding=D(1), outlineWeight=D(0))]
    pad0 = [props(top=D(0), bottom=D(0), left=D(0), right=D(0))]
    vals = table([mproj(v, lbl) for lbl, v, c, cm in items],
                 objects={"values": [props(fontSize=D(17 if n <= 7 else 15), bold=lit(True), wordWrap=lit(False))],
                          "columnHeaders": [props(fontSize=D(9), fontColor=color(T.TEXT2), backColor=color(T.BG2),
                                                  outlineStyle=D(0), autoSizeColumnWidth=lit(False), wordWrap=lit(False))],
                          "grid": nogrid, "total": [props(totals=lit(False))],
                          "columnFormatting": [props(sel_m(v), alignment=lit("Left"), styleHeader=lit(True)) for lbl, v, c, cm in items]},
                 widths={mref(v): cw for lbl, v, c, cm in items})
    vals["visualContainerObjects"] = dict(vco(bg=False, border=False, alt="Indicadores: " + ", ".join(i[0] for i in items)), padding=pad0)
    page.add(key + "_vals", x + 12, y + 10, w - 16, 62, vals)
    comps = [(c or "Período Selecionado", cm) for lbl, v, c, cm in items]
    cvals = [props(fontSize=D(9), wordWrap=lit(False), fontColorPrimary=color(T.TEXT2), fontColorSecondary=color(T.TEXT2))]
    cvals += [font_fx(c, cm) for c, cm in comps if cm]
    ct = table([mproj(c, " " * (i + 1)) for i, (c, cm) in enumerate(comps)],
               objects={"values": cvals,
                        "columnHeaders": [props(fontSize=D(1), fontColor=color(T.BG2), backColor=color(T.BG2),
                                                outlineStyle=D(0), autoSizeColumnWidth=lit(False))],
                        "grid": nogrid, "total": [props(totals=lit(False))],
                        "columnFormatting": [props(sel_m(c), alignment=lit("Left")) for c, cm in comps]},
               widths={mref(c): cw for c, cm in comps})
    ct["visualContainerObjects"] = dict(vco(bg=False, border=False), padding=pad0)
    page.add(key + "_comp", x + 12, y + 66, w - 16, 26, ct)
    for i in range(1, n):
        page.add(f"{key}_d{i}", x + 12 + i * cw - 8, y + 18, 1, h - 36, shape(T.DIVIDER))


def values_on_rows(measures, size=10, colors=None, label_w=None):
    """Lista rotulo | valor (matriz com valores em linhas). measures: (medida, rotulo)."""
    vals = [props(fontSize=D(size), valuesOnRow=lit(True))]
    for m, cm in (colors or {}).items():
        vals.append(props(sel_m(m), fontColorPrimary=color_fx(cm), fontColorSecondary=color_fx(cm)))
    o = {"values": vals,
         "columnHeaders": [props(fontSize=D(1), fontColor=color(T.BG2), outlineStyle=D(0))],
         "rowHeaders": [props(fontSize=D(size), fontColor=color(T.TEXT2), wordWrap=lit(True))],
         "grid": [props(gridHorizontal=lit(True), gridVertical=lit(False), rowPadding=D(6))],
         "subTotals": [props(rowSubtotals=lit(False), columnSubtotals=lit(False))]}
    return {"visualType": "pivotTable",
            "query": {"queryState": {"Values": {"projections": [mproj(m, lbl) for m, lbl in measures]}}},
            "objects": o}


def ref_line_today():
    return [props({"id": "1"}, show=lit(True), displayName=lit("Última venda"),
                  value={"expr": mexpr("Data Última Venda")}, dataLabelShow=lit(True),
                  shadeRegion=lit("none"), lineColor=color(T.TEXT2), style=lit("dashed"),
                  dataLabelColor=color(T.TEXT2), dataLabelText=lit("Name"))]


def line_cumulative(axis=("dCalendario", "Data")):
    series = [("Meta Acumulada", "Meta", T.MUTED, "solid", 2), ("Realizado Acumulado", "Realizado", T.PURPLE, "solid", 3),
              ("Forecast Acumulado", "Forecast", T.CYAN, "dashed", 3)]
    return {"visualType": "lineChart",
            "query": {"queryState": {"Category": {"projections": [cproj(*axis)]},
                                     "Y": {"projections": [mproj(m, d) for m, d, *_ in series]}},
                      "sortDefinition": sort_c(*axis)},
            "objects": {
                "categoryAxis": [props(axisType=lit("Scalar"), showAxisTitle=lit(False))],
                "valueAxis": [props(showAxisTitle=lit(False))],
                "lineStyles": [props(sel_m(m), strokeWidth=D(w), lineStyle=lit(st), showMarker=lit(False)) for m, d, c, st, w in series],
                "dataPoint": [props(sel_m(m), fill=color(c)) for m, d, c, st, w in series],
                "xAxisReferenceLine": ref_line_today(),
                "legend": [props(show=lit(True), position=lit("Top"))]}}


def chart(vtype, category, ys, y2=None, sort=None, objects=None, tooltips=None, field_param=None, size=None, xs=None):
    qs = {}
    if category:
        qs["Category"] = {"projections": [cproj(*category)]}
        if field_param:
            qs["Category"]["fieldParameters"] = [{"parameterExpr": cexpr(*field_param), "index": 0, "length": 1}]
    if xs:
        qs["X"] = {"projections": [mproj(*x) for x in xs]}
    qs["Y"] = {"projections": [mproj(*y) for y in ys]}
    if y2:
        qs["Y2"] = {"projections": [mproj(*y) for y in y2]}
    if size:
        qs["Size"] = {"projections": [mproj(*size)]}
    if tooltips:
        qs["Tooltips"] = {"projections": [mproj(*t) for t in tooltips]}
    q = {"queryState": qs}
    if sort:
        q["sortDefinition"] = sort
    return {"visualType": vtype, "query": q, "objects": objects or {}}


def table(columns, sort=None, objects=None, widths=None):
    """columns: lista de projecoes ja prontas (mproj/cproj)."""
    q = {"queryState": {"Values": {"projections": columns}}}
    if sort:
        q["sortDefinition"] = sort
    o = dict(objects or {})
    o.setdefault("total", [props(totals=lit(False))])
    if widths:
        o["columnWidth"] = [props({"metadata": ref}, value=D(w)) for ref, w in widths.items()]
        o.setdefault("columnHeaders", [props(autoSizeColumnWidth=lit(False))])
    return {"visualType": "tableEx", "query": q, "objects": o}


def databar(measure, pos=T.PURPLE, neg=T.CORAL):
    return props(sel_m(measure), dataBars={"positiveColor": color(pos), "negativeColor": color(neg),
                                           "axisColor": color(T.DIVIDER), "reverseDirection": lit(False),
                                           "hideText": lit(False)})


def font_fx(measure, color_measure):
    return props(dict(WILD, metadata=mref(measure)), fontColor=color_fx(color_measure))


def with_vco(v, **kw):
    v["visualContainerObjects"] = vco(**kw)
    return v
