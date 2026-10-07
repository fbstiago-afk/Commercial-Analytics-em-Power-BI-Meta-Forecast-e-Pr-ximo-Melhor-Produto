# -*- coding: utf-8 -*-
"""Revisao 2 das medidas (ranking/pareto imunes a colunas extras no visual, rotulos curtos, leitura executiva)."""
import io, os, re, uuid
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "Dashboard Comercial.SemanticModel", "definition", "tables", "Medidas.tmdl")
s = io.open(P, encoding="utf-8").read()
nl = "\r\n" if "\r\n" in s else "\n"
lines = s.split(nl)

def find(name):
    for q in (f"\tmeasure '{name}' =", f"\tmeasure {name} ="):
        for i, l in enumerate(lines):
            if l == q or l.startswith(q + " "):
                return i
    return -1

def set_expr(name, expr, folder=None, fmt=None):
    i = find(name)
    quoted = f"'{name}'" if re.search(r"[^A-Za-z0-9_]", name) else name
    head = [f"\tmeasure {quoted} ="] + ["\t\t\t" + e for e in expr] if len(expr) > 1 else [f"\tmeasure {quoted} = {expr[0]}"]
    if i >= 0:
        j = i + 1
        while j < len(lines) and (lines[j].startswith("\t\t\t") or lines[j].strip() in ("", "```")) and not re.match(r"^\t\t[A-Za-z]", lines[j]):
            if lines[j].strip() == "" and j + 1 < len(lines) and re.match(r"^\t\t[A-Za-z]", lines[j + 1]):
                break
            j += 1
        lines[i:j] = head
    else:
        k = next(n for n, l in enumerate(lines) if l.startswith("\tpartition "))
        blk = head + [f"\t\tdisplayFolder: {folder}"] + ([f"\t\tformatString: {fmt}"] if fmt else []) + [f"\t\tlineageTag: {uuid.uuid4()}", ""]
        lines[k:k] = blk

def tab_prod(col="@Fat"):
    return f'CALCULATETABLE ( ADDCOLUMNS ( VALUES ( dProduto[descricao] ), "{col}", [Faturamento] ), ALLSELECTED ( dProduto ) )'

set_expr("Rank Vendedor", [
    "VAR vAtual = [Faturamento]",
    "VAR vVendedores =",
    '    CALCULATETABLE ( ADDCOLUMNS ( VALUES ( dVendedor[descricao] ), "@Fat", [Faturamento] ), ALLSELECTED ( dVendedor ) )',
    "RETURN",
    "    IF ( NOT ISBLANK ( vAtual ), COUNTROWS ( FILTER ( vVendedores, [@Fat] > vAtual ) ) + 1 )"])
set_expr("Rank Produto", [
    "VAR vAtual = [Faturamento]", "VAR vProdutos = " + tab_prod(), "RETURN",
    "    IF ( NOT ISBLANK ( vAtual ), COUNTROWS ( FILTER ( vProdutos, [@Fat] > vAtual ) ) + 1 )"])
set_expr("Pareto %", [
    "VAR vAtual = [Faturamento]", "VAR vProdutos = " + tab_prod(), "RETURN",
    "    IF (", "        NOT ISBLANK ( vAtual ),",
    "        DIVIDE ( SUMX ( FILTER ( vProdutos, [@Fat] >= vAtual ), [@Fat] ), SUMX ( vProdutos, [@Fat] ) )", "    )"])
set_expr("Share Top 10 %", [
    "VAR vProdutos = " + tab_prod(), "RETURN",
    "    DIVIDE ( SUMX ( TOPN ( 10, vProdutos, [@Fat] ), [@Fat] ), SUMX ( vProdutos, [@Fat] ) )"])
set_expr("Participação Média %", [
    "VAR vProdutos = " + tab_prod(), "RETURN",
    "    DIVIDE ( 1, COUNTROWS ( FILTER ( vProdutos, NOT ISBLANK ( [@Fat] ) ) ) )"])
set_expr("Quadrante Produto", [
    "VAR vShare = [Participação %]", "VAR vCresc = [YoY %]",
    "VAR vCrescTotal = [YoY Total Produtos %]", "VAR vShareMedio = [Participação Média %]", "RETURN",
    "    SWITCH (", "        TRUE (),", "        ISBLANK ( vShare ), BLANK (),",
    '        ISBLANK ( vCresc ), "Novo no período",',
    '        vCresc >= vCrescTotal && vShare >= vShareMedio, "Estrela",',
    '        vCresc >= vCrescTotal, "Crescimento",', '        vShare >= vShareMedio, "Atenção",',
    '        "Baixa relevância"', "    )"])

def arrow(m, suffix):
    return [f"VAR v = {m}", "RETURN",
            f'    IF ( NOT ISBLANK ( v ), IF ( v >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( v ), "0.0%" ) & "{suffix}" )']
set_expr("Rótulo Forecast", ["VAR v = [Atingimento Forecast %]", "RETURN",
                             '    IF ( NOT ISBLANK ( v ), IF ( v >= 1, "▲ ", "▼ " ) & FORMAT ( v, "0.0%" ) & " da meta" )'])
set_expr("Rótulo Gap Previsto", arrow("[Forecast x Meta %]", " vs meta"))
set_expr("Rótulo Ritmo Original", arrow("[Ritmo vs Original %]", " vs original"))
set_expr("Rótulo Ritmo", ["VAR v = [Ritmo vs Necessário %]", "RETURN", "    IF (", "        NOT ISBLANK ( v ),",
                          '        IF ( v >= 0, "▲ suficiente (", "▼ insuficiente (" ) & FORMAT ( v, "+0.0%;-0.0%" ) & ")"', "    )"])
set_expr("Rótulo Dias Corridos", ['[Dias Restantes] & " dias corridos"'])
set_expr("Rótulo Dias Período", ['[Dias Úteis] & " dias úteis"'])
set_expr("Rótulo Dias Decorridos", ['[Dias Úteis Decorridos] & " dias úteis decorridos"'])
set_expr("Rótulo Sem Recompra", ['"ativos só no ano anterior"'])
set_expr("Rótulo Concentração", ['"share dos 10 maiores"'])
set_expr("Rótulo Risco", ["VAR v = [Faturamento 12M em Risco]", "RETURN",
                          '    "R$ " & IF ( v >= 1E6, FORMAT ( v / 1E6, "#,0.00" ) & " Mi", FORMAT ( v / 1E3, "#,0.0" ) & " mil" ) & " em 12 meses"'])
set_expr("Rótulo SKUs", ['[SKUs Vendidos] & " SKUs vendidos"'])
set_expr("Rótulo Classe A", ['[Produtos Classe A] & " produtos somam 80%"'])
set_expr("Rótulo Vendedores", ['"de " & [Vendedores Ativos] & " vendedores"'])
set_expr("Rótulo Mix", ['"SKUs distintos"'])
set_expr("Rótulo Recomendados", ['"SKUs com score"'])
set_expr("Leitura Executiva", [
    '"▸ META  —  " & [Insight Meta] & UNICHAR ( 10 )',
    '    & "▸ FORECAST  —  " & [Insight Forecast] & UNICHAR ( 10 )',
    '    & "▸ RITMO  —  " & [Insight Ritmo] & UNICHAR ( 10 )',
    '    & "▸ VENDEDORES  —  " & [Insight Vendedor] & UNICHAR ( 10 )',
    '    & "▸ PRODUTOS  —  " & [Insight Produto]'], folder="09 UX\\Insights")
set_expr("Cidade Cliente", ['IF ( HASONEVALUE ( dCliente[id] ), SELECTEDVALUE ( dCliente[cidade] ) & "/" & SELECTEDVALUE ( dCliente[uf] ) )'],
         folder="07 Recomendação\\Perfil")
set_expr("Primeira Compra Cliente", ["IF ( HASONEVALUE ( dCliente[id] ), SELECTEDVALUE ( dCliente[Primeira Compra] ) )"],
         folder="07 Recomendação\\Perfil", fmt="dd/MM/yyyy")
s = nl.join(lines)
old = "        vCross & vRec"
assert old in s
s = s.replace(old, '        vCross & vRec\n\t\t\t            & IF ( NOT ISBLANK ( [Ação Segmento] ), " Postura para o segmento " & [Segmento Cliente] & ": " & [Ação Segmento] )'.replace("\n", nl), 1) if "Postura para o segmento" not in s else s
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("ok", len(re.findall(r"^\tmeasure ", s, flags=re.M)))
