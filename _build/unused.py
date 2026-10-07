# -*- coding: utf-8 -*-
"""Lista medidas que nao aparecem em nenhum visual nem em outra medida (candidatas a limpeza)."""
import io, os, re, glob, json
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = io.open(os.path.join(base, "Dashboard Comercial.SemanticModel", "definition", "tables", "Medidas.tmdl"), encoding="utf-8").read()
names = [m.group(1) or m.group(2) for m in re.finditer(r"^\tmeasure (?:'([^']+)'|(\S+)) =", s, flags=re.M)]
rep = ""
for f in glob.glob(os.path.join(base, "Dashboard Comercial.Report", "definition", "**", "*.json"), recursive=True):
    rep += io.open(f, encoding="utf-8").read()
for n in names:
    in_rep = f'"Property": "{n}"' in rep
    in_dax = len(re.findall(re.escape(f"[{n}]"), s)) > 0
    if not in_rep and not in_dax:
        print(n)
