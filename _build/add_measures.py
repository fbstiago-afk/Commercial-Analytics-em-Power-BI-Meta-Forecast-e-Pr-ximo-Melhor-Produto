# -*- coding: utf-8 -*-
"""Acrescenta medidas de rotulo (UX) ao TMDL e corrige os format strings dinamicos. Executar com o Desktop fechado."""
import io, os, re, uuid
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "Dashboard Comercial.SemanticModel", "definition", "tables", "Medidas.tmdl")
s = io.open(P, encoding="utf-8").read()
nl = "\r\n" if "\r\n" in s else "\n"

# 1) format strings: as virgulas de escala precisam ficar imediatamente antes do separador decimal
s = s.replace("#,0.00,, \\M\\i", "#,0,,.00 \\M\\i").replace("#,0.0, \\m\\i\\l", "#,0,.0 \\m\\i\\l")

def money(v):
    return f'IF ( ABS ( {v} ) >= 1E6, FORMAT ( {v} / 1E6, "#,0.00" ) & " Mi", FORMAT ( {v} / 1E3, "#,0.0" ) & " mil" )'

def arrow(m, suffix):
    return [f"VAR v = {m}", "RETURN",
            f'    IF ( NOT ISBLANK ( v ), IF ( v >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( v ), "0.0%" ) & "{suffix}" )']

NEW = {
    "Rótulo LY": ["VAR v = [YoY Δ]", "RETURN",
                  '    IF ( NOT ISBLANK ( v ), IF ( v >= 0, "▲ +R$ ", "▼ −R$ " ) & ' + money("ABS ( v )").replace("ABS ( ABS ( v ) )", "ABS ( v )") + ' & " vs ano anterior" )'],
    "Rótulo LM": ["VAR v = [Faturamento LM]", "RETURN", '    IF ( NOT ISBLANK ( v ), "base: R$ " & ' + money("v") + " )"],
    "Rótulo Vendedores": ['"de " & [Vendedores Ativos] & " vendedores com venda"'],
    "Rótulo Dias Período": ['[Dias Úteis] & " dias úteis no período"'],
    "Rótulo Gap Previsto": arrow("[Forecast x Meta %]", " vs meta do período"),
    "Rótulo Dias Corridos": ['[Dias Restantes] & " dias corridos restantes"'],
    "Rótulo Ritmo Original": arrow("[Ritmo vs Original %]", " vs meta diária original"),
    "Rótulo Dias Decorridos": ['[Dias Úteis Decorridos] & " dias úteis decorridos"'],
    "Rótulo SKUs": ['[SKUs Vendidos] & " SKUs (produto + tamanho)"'],
    "Rótulo Itens Pedido": ['FORMAT ( [Itens por Pedido], "#,0.0" ) & " itens por nota"'],
    "Rótulo Classe A": ['[Produtos Classe A] & " produtos somam 80% (classe A)"'],
    "Rótulo Margem": ["VAR v = [Margem Bruta]", "RETURN", '    IF ( NOT ISBLANK ( v ), "margem bruta R$ " & ' + money("v") + " )"],
    "Rótulo Novos": ['FORMAT ( DIVIDE ( [Clientes Novos], [Clientes] ), "0.0%" ) & " dos clientes ativos"'],
    "Rótulo Sem Recompra": ['"compraram no ano anterior e não agora"'],
    "Rótulo Concentração": ['"participação dos 10 maiores clientes"'],
    "Rótulo Risco": ["VAR v = [Faturamento 12M em Risco]", "RETURN", '    "R$ " & ' + money("v") + ' & " de faturamento 12M"'],
    "Rótulo Carteira": ['[Clientes na Carteira] & " clientes na carteira"'],
    "Rótulo Segmento": ['"segmento " & [Segmento Cliente]'],
    "Rótulo Ticket 12M": ["VAR v = [Ticket Médio 12M]", "RETURN", '    IF ( NOT ISBLANK ( v ), "ticket médio R$ " & FORMAT ( v, "#,0" ) )'],
    "Rótulo Mix": ['"SKUs distintos em 12 meses"'],
    "Rótulo Recência": ["VAR v = [Recência Cliente (dias)]", "RETURN", '    IF ( NOT ISBLANK ( v ), "há " & v & " dias" )'],
    "Rótulo Similaridade": ["VAR v = [Similaridade]", "RETURN",
                            '    IF ( NOT ISBLANK ( v ), "similaridade média " & FORMAT ( v, "0%" ), "sem similares ≥ 50%" )'],
    "Rótulo Recomendados": ['"SKUs com score no período"'],
    "Cor MoM": ['IF ( [MoM %] >= 0, "#39D98A", "#FF7A68" )'],
    "Cor Neutra": ['"#AEB8CF"'],
    "Cor ABC": ['SWITCH ( [Classe ABC], "A", "#6957FF", "B", "#8B5CF6", "#6B7694" )'],
}
FOLDER = {"Cor MoM": "09 UX\\Cores", "Cor Neutra": "09 UX\\Cores", "Cor ABC": "09 UX\\Cores"}
blocks = []
for name, lines in NEW.items():
    if f"measure '{name}'" in s:
        continue
    b = [f"\tmeasure '{name}' ="] + ["\t\t\t" + l for l in lines] if len(lines) > 1 else [f"\tmeasure '{name}' = {lines[0]}"]
    b += [f"\t\tdisplayFolder: {FOLDER.get(name, chr(48) + '9 UX' + chr(92) + 'Rótulos')}", f"\t\tlineageTag: {uuid.uuid4()}", ""]
    blocks.append(nl.join(b))
i = s.index("\tpartition ")
s = s[:i] + nl.join(blocks) + (nl if blocks else "") + s[i:]
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("medidas adicionadas:", len(blocks), "| total:", len(re.findall(r"^\tmeasure ", s, flags=re.M)))
