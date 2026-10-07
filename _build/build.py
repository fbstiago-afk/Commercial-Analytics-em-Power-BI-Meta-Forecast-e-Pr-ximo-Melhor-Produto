# -*- coding: utf-8 -*-
"""Gera o relatorio PBIR do Commercial Analytics a partir dos componentes.
Uso: python3 _build/build.py   (executar com o Power BI Desktop FECHADO)"""
import json, os, shutil, sys
from pbir import *
from components import *
import tokens as T
import pages

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(os.path.dirname(HERE), "Dashboard Comercial.Report")
DEF = os.path.join(ROOT, "definition")
RES = os.path.join(ROOT, "StaticResources", "RegisteredResources")


def main():
    only = sys.argv[1:]
    # 1) tema centralizado
    os.makedirs(RES, exist_ok=True)
    for f in os.listdir(RES):
        os.remove(os.path.join(RES, f))
    theme_file = T.THEME_NAME + ".json"
    dump(os.path.join(RES, theme_file), T.theme())

    # 2) report.json: troca o tema, remove recursos e visuais customizados do layout antigo
    rp = os.path.join(DEF, "report.json")
    rep = json.load(open(rp, encoding="utf-8-sig"))
    rep["themeCollection"]["customTheme"] = {"name": theme_file,
                                             "reportVersionAtImport": rep["themeCollection"]["baseTheme"]["reportVersionAtImport"],
                                             "type": "RegisteredResources"}
    rep.pop("publicCustomVisuals", None)
    for pkg in rep["resourcePackages"]:
        if pkg["name"] == "RegisteredResources":
            pkg["items"] = [{"name": theme_file, "path": theme_file, "type": "CustomTheme"}]
    rep["filterConfig"]["filters"] = [f for f in rep["filterConfig"]["filters"] if f.get("displayName")]
    dump(rp, rep)

    # 3) paginas: remove as antigas e grava as novas
    pdir = os.path.join(DEF, "pages")
    built = pages.build_all(ROOT)
    keep = {p.name for p in built}
    for d in os.listdir(pdir):
        full = os.path.join(pdir, d)
        if os.path.isdir(full) and (d not in keep or not only or d in only):
            shutil.rmtree(full)
    for p in built:
        if not only or p.name in only:
            p.write(T.BG if not p.tooltip else T.ELEVATED)
    dump(os.path.join(pdir, "pages.json"),
         {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
          "pageOrder": [p.name for p in built], "activePageName": built[0].name})

    # 4) bookmarks do layout antigo nao sao mais usados
    bdir = os.path.join(DEF, "bookmarks")
    if os.path.isdir(bdir):
        shutil.rmtree(bdir)
    print("paginas:", [(p.name, len(p.visuals)) for p in built])


if __name__ == "__main__":
    main()
