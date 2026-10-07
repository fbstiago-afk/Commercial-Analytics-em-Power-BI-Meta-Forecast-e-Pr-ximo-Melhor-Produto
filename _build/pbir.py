# -*- coding: utf-8 -*-
"""Helpers para gerar arquivos PBIR (visual.json / page.json) do Dashboard Comercial.
Design tokens ficam em tokens.py; o tema JSON e a unica fonte de estilo padrao."""
import hashlib, json, os

SCHEMA_VISUAL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.13.0/schema.json"
SCHEMA_PAGE = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
M = "Medidas"


def uid(*parts):
    return hashlib.md5("|".join(parts).encode("utf-8")).hexdigest()[:20]


def lit(v):
    if isinstance(v, bool):
        s = "true" if v else "false"
    elif isinstance(v, int):
        s = f"{v}L"
    elif isinstance(v, float):
        s = f"{v:g}D"
    else:
        s = "'" + str(v).replace("'", "''") + "'"
    return {"expr": {"Literal": {"Value": s}}}


def D(v):
    return {"expr": {"Literal": {"Value": f"{v:g}D"}}}


def color(hexv):
    return {"solid": {"color": lit(hexv)}}


def mexpr(name, entity=M):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": name}}


def cexpr(entity, name):
    return {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": name}}


def color_fx(measure):
    return {"solid": {"color": {"expr": mexpr(measure)}}}


def mref(name):
    return f"{M}.{name}"


def mproj(name, display=None):
    p = {"field": mexpr(name), "queryRef": mref(name), "nativeQueryRef": display or name}
    if display:
        p["displayName"] = display
    return p


def cproj(entity, name, display=None, active=True):
    p = {"field": cexpr(entity, name), "queryRef": f"{entity}.{name}", "nativeQueryRef": display or name}
    if active:
        p["active"] = True
    if display:
        p["displayName"] = display
    return p


def props(sel=None, **kw):
    d = {"properties": kw}
    if sel is not None:
        d["selector"] = sel
    return d


def sel_m(name):
    return {"metadata": mref(name)}


WILD = {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}


def sort_m(name, desc=True):
    return {"sort": [{"field": mexpr(name), "direction": "Descending" if desc else "Ascending"}]}


def sort_c(entity, name, desc=False):
    return {"sort": [{"field": cexpr(entity, name), "direction": "Descending" if desc else "Ascending"}]}


def vco(title=None, title_m=None, title_size=None, title_color=None, bg=None, bg_color=None, border=None,
        radius=None, alt=None, tooltip=None, pad=None, subtitle=None, subtitle_m=None, sub_color_m=None, header=None):
    """visualContainerObjects. O tema define o padrao; aqui so entram excecoes."""
    o = {}
    if title is not None or title_m is not None:
        t = {"show": lit(True), "text": lit(title) if title is not None else {"expr": mexpr(title_m)}}
        if title_size:
            t["fontSize"] = D(title_size)
        if title_color:
            t["fontColor"] = color(title_color)
        o["title"] = [props(**t)]
    elif title is None and title_m is None:
        o["title"] = [props(show=lit(False))]
    if subtitle is not None or subtitle_m is not None:
        s = {"show": lit(True), "text": lit(subtitle) if subtitle is not None else {"expr": mexpr(subtitle_m)}}
        if sub_color_m:
            s["fontColor"] = color_fx(sub_color_m)
        o["subTitle"] = [props(**s)]
    if bg is not None:
        b = {"show": lit(bool(bg))}
        if bg_color:
            b["color"] = color(bg_color)
            b["transparency"] = D(0)
        o["background"] = [props(**b)]
    if border is not None:
        b = {"show": lit(bool(border))}
        if isinstance(border, str):
            b["color"] = color(border)
        if radius is not None:
            b["radius"] = D(radius)
        o["border"] = [props(**b)]
    if alt:
        o["general"] = [props(altText=lit(alt))]
    if tooltip:
        o["visualTooltip"] = [props(show=lit(True), type=lit("Canvas"), section=lit(tooltip))]
    if pad is not None:
        o["padding"] = [props(top=D(pad[0]), right=D(pad[1]), bottom=D(pad[2]), left=D(pad[3]))]
    return o


class Page:
    def __init__(self, root, name, display, width=1440, height=810, tooltip=False, hidden=False):
        self.root, self.name, self.display = root, name, display
        self.width, self.height, self.tooltip, self.hidden = width, height, tooltip, hidden
        self.visuals, self.interactions, self.n = [], [], 0

    def add(self, key, x, y, w, h, visual, filters=None, hidden=False):
        self.n += 1
        name = uid(self.name, key)
        d = {"$schema": SCHEMA_VISUAL, "name": name,
             "position": {"x": x, "y": y, "z": self.n * 1000, "height": h, "width": w, "tabOrder": self.n * 1000},
             "visual": visual}
        visual.setdefault("drillFilterOtherVisuals", True)
        if filters:
            d["filterConfig"] = {"filters": filters}
        if hidden:
            d["isHidden"] = True
        self.visuals.append(d)
        return name

    def no_filter(self, source, target):
        self.interactions.append({"source": source, "target": target, "type": "NoFilter"})

    def write(self, bg):
        pdir = os.path.join(self.root, "definition", "pages", self.name)
        os.makedirs(os.path.join(pdir, "visuals"), exist_ok=True)
        page = {"$schema": SCHEMA_PAGE, "name": self.name, "displayName": self.display,
                "displayOption": "FitToPage", "height": self.height, "width": self.width,
                "objects": {"background": [props(color=color(bg), transparency=D(0))],
                            "outspace": [props(color=color("#0B1220"), transparency=D(0))]}}
        if self.interactions:
            page["visualInteractions"] = self.interactions
        if self.tooltip:
            page["type"] = "Tooltip"
            page["visibility"] = "HiddenInViewMode"
        elif self.hidden:
            page["visibility"] = "HiddenInViewMode"
        dump(os.path.join(pdir, "page.json"), page)
        for v in self.visuals:
            vd = os.path.join(pdir, "visuals", v["name"])
            os.makedirs(vd, exist_ok=True)
            dump(os.path.join(vd, "visual.json"), v)


def dump(path, obj):
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def measure_filter(name, value=1, kind=0):
    """Filtro de visual: medida = value (ComparisonKind 0 = igual, 1 = maior que)."""
    return {"name": "Filter" + uid("f", name, str(value)), "field": mexpr(name), "type": "Advanced",
            "filter": {"Version": 2, "From": [{"Name": "m", "Entity": M, "Type": 0}],
                       "Where": [{"Condition": {"Comparison": {
                           "ComparisonKind": kind,
                           "Left": {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": name}},
                           "Right": {"Literal": {"Value": f"{value}L"}}}}}]},
            "howCreated": "User"}


def slicer_filter(entity, column, value):
    return {"filter": {"Version": 2, "From": [{"Name": "t", "Entity": entity, "Type": 0}],
                       "Where": [{"Condition": {"In": {
                           "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": column}}],
                           "Values": [[{"Literal": {"Value": "'" + value.replace("'", "''") + "'"}}]]}}}]}}
