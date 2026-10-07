# -*- coding: utf-8 -*-
"""Design tokens do Commercial Analytics (Dark Premium). Fonte unica de cores, grid e tipografia."""
BG = "#111827"          # fundo da pagina
BG2 = "#182033"         # superficie padrao dos visuais / rail
SURFACE = "#202A44"     # elementos sobre a superficie (slicers, hover)
ELEVATED = "#27324F"    # tooltips, trilhas de barras
PURPLE = "#6957FF"      # cor primaria (realizado, foco)
PURPLE2 = "#8B5CF6"     # acento
CYAN = "#22C7BE"        # destaque secundario (forecast)
GREEN = "#39D98A"       # positivo
AMBER = "#F5B942"       # atencao
CORAL = "#FF7A68"       # negativo
RED = "#F45B69"
TEXT = "#F8FAFC"
TEXT2 = "#AEB8CF"
MUTED = "#6B7694"       # contexto / referencia (meta, ano anterior)
DIVIDER = "#263150"     # ~ rgba(255,255,255,.08) sobre BG2

FONT = "Segoe UI"
FONT_SB = "'Segoe UI Semibold', wf_segoe-ui_semibold, helvetica, arial, sans-serif"

W, H = 1440, 810
RAIL = 168
MARGIN = 24
GAP = 16
X0 = RAIL + MARGIN            # 192
CW = W - X0 - MARGIN          # 1224 de largura util
RADIUS = 12

THEME_NAME = "CommercialAnalyticsDark"


def theme():
    def c(h):
        return {"solid": {"color": h}}
    axis = {"show": True, "showAxisTitle": False, "labelColor": c(TEXT2), "fontSize": 9, "fontFamily": FONT,
            "gridlineShow": False}
    vaxis = {"show": True, "showAxisTitle": False, "labelColor": c(TEXT2), "fontSize": 9, "fontFamily": FONT,
             "gridlineShow": True, "gridlineColor": c(DIVIDER), "gridlineStyle": "solid", "gridlineThickness": 1}
    legend = {"show": True, "position": "Top", "labelColor": c(TEXT2), "fontSize": 9, "fontFamily": FONT,
              "showTitle": False}
    labels = {"color": c(TEXT), "fontSize": 9, "fontFamily": FONT, "enableBackground": False, "labelDisplayUnits": 1}
    cart = {"categoryAxis": [axis], "valueAxis": [vaxis], "legend": [legend], "labels": [labels]}
    table = {
        "grid": [{"gridHorizontal": True, "gridHorizontalColor": c(DIVIDER), "gridHorizontalWeight": 1,
                  "gridVertical": False, "rowPadding": 5, "outlineColor": c(DIVIDER), "textSize": 9}],
        "columnHeaders": [{"fontColor": c(TEXT2), "backColor": c(BG2), "outline": "BottomOnly",
                           "outlineStyle": 1, "fontSize": 9, "fontFamily": FONT, "bold": False, "wordWrap": True}],
        "values": [{"fontColorPrimary": c(TEXT), "backColorPrimary": c(BG2), "fontColorSecondary": c(TEXT),
                    "backColorSecondary": c(BG2), "outline": "None", "fontSize": 9, "fontFamily": FONT,
                    "wordWrap": True}],
        "total": [{"totals": False, "fontColor": c(TEXT), "backColor": c(BG2)}],
        "rowHeaders": [{"fontColor": c(TEXT2), "backColor": c(BG2), "outline": "None", "fontSize": 9,
                        "fontFamily": FONT, "wordWrap": True, "showExpandCollapseButtons": False}],
        "subTotals": [{"rowSubtotals": False, "columnSubtotals": False}],
        "stylePreset": [{"name": "None"}],
    }
    return {
        "name": THEME_NAME,
        "dataColors": [PURPLE, CYAN, PURPLE2, GREEN, AMBER, CORAL, MUTED, RED],
        "background": BG2, "foreground": TEXT, "tableAccent": PURPLE,
        "good": GREEN, "neutral": AMBER, "bad": CORAL,
        "maximum": PURPLE, "center": PURPLE2, "minimum": ELEVATED, "null": MUTED,
        "firstLevelElements": TEXT, "secondLevelElements": TEXT2, "thirdLevelElements": DIVIDER,
        "fourthLevelElements": MUTED, "secondaryBackground": SURFACE,
        "hyperlink": CYAN, "visitedHyperlink": PURPLE2,
        "textClasses": {
            "callout": {"fontSize": 22, "fontFace": "Segoe UI Semibold", "color": TEXT},
            "title": {"fontSize": 11, "fontFace": "Segoe UI Semibold", "color": TEXT},
            "header": {"fontSize": 10, "fontFace": "Segoe UI Semibold", "color": TEXT},
            "label": {"fontSize": 9, "fontFace": "Segoe UI", "color": TEXT2},
        },
        "visualStyles": {
            "*": {"*": {
                "background": [{"show": True, "color": c(BG2), "transparency": 0}],
                "border": [{"show": True, "color": c(BG2), "radius": RADIUS, "width": 1}],
                "dropShadow": [{"show": False}],
                "title": [{"show": True, "fontColor": c(TEXT), "fontSize": 11, "fontFamily": FONT_SB,
                           "titleWrap": True, "alignment": "left", "background": c(BG2)}],
                "subTitle": [{"show": False, "fontColor": c(TEXT2), "fontSize": 9, "fontFamily": FONT,
                              "titleWrap": True}],
                "divider": [{"show": False}],
                "padding": [{"top": 12, "bottom": 12, "left": 14, "right": 14}],
                "visualHeader": [{"show": False}],
                "visualTooltip": [{"type": "Default", "background": c(ELEVATED), "titleFontColor": c(TEXT2),
                                   "valueFontColor": c(TEXT), "fontSize": 9, "fontFamily": FONT,
                                   "transparency": 0}],
                "outspacePane": [{"backgroundColor": c(BG2), "foregroundColor": c(TEXT), "transparency": 0,
                                  "border": True, "borderColor": c(DIVIDER)}],
                "filterCard": [{"$id": "Applied", "backgroundColor": c(SURFACE), "foregroundColor": c(TEXT),
                                "transparency": 0},
                               {"$id": "Available", "backgroundColor": c(BG2), "foregroundColor": c(TEXT),
                                "transparency": 0}],
            }},
            "page": {"*": {
                "background": [{"color": c(BG), "transparency": 0}],
                "outspace": [{"color": c("#0B1220"), "transparency": 0}],
            }},
            "lineChart": {"*": dict(cart, lineStyles=[{"strokeWidth": 3, "showMarker": False,
                                                       "lineStyle": "solid"}])},
            "clusteredColumnChart": {"*": cart},
            "clusteredBarChart": {"*": dict(cart, valueAxis=[dict(vaxis, show=False, gridlineShow=False)])},
            "lineClusteredColumnComboChart": {"*": dict(cart, lineStyles=[{"strokeWidth": 2, "showMarker": True,
                                                                           "markerSize": 4}])},
            "scatterChart": {"*": dict(cart, categoryAxis=[dict(axis, gridlineShow=True, gridlineColor=c(DIVIDER))],
                                       bubbles=[{"bubbleSize": -10}],
                                       categoryLabels=[{"show": False, "color": c(TEXT2), "fontSize": 8}],
                                       fillPoint=[{"show": True}])},
            "tableEx": {"*": table},
            "pivotTable": {"*": table},
            "slicer": {"*": {
                "background": [{"show": False}],
                "border": [{"show": False}],
                "padding": [{"top": 0, "bottom": 0, "left": 0, "right": 0}],
                "header": [{"show": True, "fontColor": c(TEXT2), "textSize": 8, "fontFamily": FONT,
                            "background": c(BG)}],
                "items": [{"fontColor": c(TEXT), "background": c(SURFACE), "textSize": 9, "fontFamily": FONT,
                           "outline": "None"}],
                "selection": [{"selectAllCheckboxEnabled": False}],
            }},
            "card": {"*": {
                "labels": [{"color": c(TEXT), "fontSize": 20, "fontFamily": FONT_SB}],
                "categoryLabels": [{"show": False, "color": c(TEXT2), "fontSize": 9}],
            }},
            "cardVisual": {"*": {
                "background": [{"show": False}],
                "border": [{"show": False}],
                "padding": [{"top": 0, "bottom": 0, "left": 0, "right": 0}],
            }},
            "textbox": {"*": {"background": [{"show": False}], "border": [{"show": False}],
                              "padding": [{"top": 0, "bottom": 0, "left": 0, "right": 0}]}},
            "shape": {"*": {"padding": [{"top": 0, "bottom": 0, "left": 0, "right": 0}]}},
            "actionButton": {"*": {"background": [{"show": False}], "border": [{"show": False}],
                                   "padding": [{"top": 0, "bottom": 0, "left": 0, "right": 0}]}},
        },
    }
