
import re
import unicodedata

from database import (
    resumir_situacoes,
    buscar_ingresso,
    listar_ingressos,
)


def normalizar(texto: str) -> str:
    """Remove acentos, pontuação e diferenças entre maiúsculas/minúsculas."""
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )
    texto = re.sub(r"[^\w\s]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def consultar_por_codigo(codigo: str) -> dict:
    ingresso = buscar_ingresso(codigo.strip())

    if ingresso is None:
        return {"encontrado": False, "codigo": codigo}

    return {
        "encontrado": True,
        "codigo": ingresso[0],
        "idade": ingresso[1],
        "situacao": ingresso[2],
    }


def listar_por_situacao(situacao: str) -> list:
    return [
        {
            "codigo": codigo,
            "idade": idade,
            "situacao": status,
        }
        for codigo, idade, status in listar_ingressos()
        if status == situacao
    ]


def perguntar(pergunta: str) -> str:
    """Interpreta perguntas sobre os ingressos usando o banco local."""

    if not isinstance(pergunta, str) or not pergunta.strip():
        return "Digite uma pergunta sobre os ingressos."

    texto = normalizar(pergunta)
    ingressos = listar_ingressos()

    # 1. Consulta específica por código
    codigos = re.findall(r"\b[A-Z]{3}\d{3}\b", pergunta.upper())

    if codigos:
        codigo = codigos[0]
        ingresso = consultar_por_codigo(codigo)

        if not ingresso["encontrado"]:
            return f"O ingresso {codigo} não foi encontrado."

        situacao = ingresso["situacao"]

        if any(p in texto for p in [
            "ja entrou", "ja entraram", "entrou", "entraram",
            "presente", "chegou", "dentro", "fora",
            "compareceu"
        ]):
            if situacao == "dentro":
                return f"Sim. O ingresso {codigo} já entrou e está presente."
            return f"Não. O ingresso {codigo} ainda está fora do evento."

        return (
            f"Ingresso: {codigo}\n"
            f"Situação: {situacao}\n"
            f"Idade cadastrada: {ingresso['idade']} anos."
        )

    # 2. Detectar filtros de idade
    idade_limite = None
    operador = None

    # Ex.: "20 anos ou mais", "20 anos ou menos"
    resultado = re.search(
        r"\b(\d+)\s+anos?\s+ou\s+(mais|menos)\b",
        texto,
    )

    if resultado:
        idade_limite = int(resultado.group(1))
        operador = ">=" if resultado.group(2) == "mais" else "<="

    else:
        padroes_idade = [
            (r"\b(?:exatamente|exato|exatos|com idade de|idade de)\s+(\d+)(?:\s+anos?)?\b", "=="),
            (r"\b(?:menos de|abaixo de|menor que|menores que|inferior a)\s+(\d+)(?:\s+anos?)?\b", "<"),
            (r"\b(?:mais de|acima de|maior que|maiores que|superior a)\s+(\d+)(?:\s+anos?)?\b", ">"),
            (r"\b(?:pelo menos|no minimo|a partir de)\s+(\d+)(?:\s+anos?)?\b", ">="),
            (r"\b(?:no maximo|ate)\s+(\d+)(?:\s+anos?)?\b", "<="),
        ]

        for padrao, op in padroes_idade:
            resultado = re.search(padrao, texto)
            if resultado:
                idade_limite = int(resultado.group(1))
                operador = op
                break

    menciona_fora = any(p in texto for p in [
        "fora", "ausente", "ausentes", "nao chegou",
        "nao chegaram", "nao entrou", "nao entraram"
    ])

    menciona_dentro = any(p in texto for p in [
        "dentro", "presente", "presentes", "ja entrou",
        "ja entraram", "compareceu", "compareceram"
    ])

    # 3. Aplicar filtros de idade e situação
    if idade_limite is not None:
        if operador == "==":
            encontrados = [i for i in ingressos if i[1] == idade_limite]
            descricao = f"exatamente {idade_limite} anos"
        elif operador == "<":
            encontrados = [i for i in ingressos if i[1] < idade_limite]
            descricao = f"menos de {idade_limite} anos"
        elif operador == ">":
            encontrados = [i for i in ingressos if i[1] > idade_limite]
            descricao = f"mais de {idade_limite} anos"
        elif operador == "<=":
            encontrados = [i for i in ingressos if i[1] <= idade_limite]
            descricao = f"{idade_limite} anos ou menos"
        else:
            encontrados = [i for i in ingressos if i[1] >= idade_limite]
            descricao = f"{idade_limite} anos ou mais"

        if menciona_fora and not menciona_dentro:
            encontrados = [i for i in encontrados if i[2] == "fora"]
            descricao += " e fora do evento"
        elif menciona_dentro and not menciona_fora:
            encontrados = [i for i in encontrados if i[2] == "dentro"]
            descricao += " e presentes"

        quer_listar = any(p in texto for p in [
            "quais", "quem", "liste", "listar", "mostre", "mostrar", "lista"
        ])

        if quer_listar:
            if not encontrados:
                return f"Não há pessoas com {descricao}."

            return (
                f"Pessoas com {descricao}:\n"
                + "\n".join(
                    f"- {i[0]} (idade: {i[1]}, situação: {i[2]})"
                    for i in encontrados
                )
            )

        return f"Há {len(encontrados)} pessoas com {descricao}."

    # 4. Identificar pedidos de listagem por situação
    quer_listar = any(p in texto for p in [
        "liste", "listar", "listagem", "quais",
        "mostre", "mostrar", "quem", "lista",
        "me diga", "me fale"
    ])

    if quer_listar and menciona_fora and not menciona_dentro:
        encontrados = listar_por_situacao("fora")

        if not encontrados:
            return "Não há ingressos fora do evento."

        return "Ingressos fora do evento:\n" + "\n".join(
            f"- {i['codigo']} (idade: {i['idade']})"
            for i in encontrados
        )

    if quer_listar and menciona_dentro and not menciona_fora:
        encontrados = listar_por_situacao("dentro")

        if not encontrados:
            return "Não há ingressos dentro do evento."

        return "Ingressos presentes:\n" + "\n".join(
            f"- {i['codigo']} (idade: {i['idade']})"
            for i in encontrados
        )

    # 5. Perguntas sobre quantidade e presença
    quer_contar = any(p in texto for p in [
        "quantos", "quantas", "quantidade", "total",
        "tem quantas", "tem quantos", "numero de",
        "número de"
    ])

    pergunta_total = any(p in texto for p in [
        "total", "cadastrado", "cadastrados",
        "no evento", "na festa", "da festa",
        "no sistema", "ao todo", "todas as pessoas",
        "todos os ingressos"
    ])

    if quer_contar or pergunta_total or any(p in texto for p in [
        "quem ainda nao chegou", "quem nao chegou",
        "tem alguem", "ha pessoas", "quantas pessoas tem"
    ]):
        resumo = resumir_situacoes() or {}
        dentro = resumo.get("dentro", 0)
        fora = resumo.get("fora", 0)
        total = dentro + fora

        if menciona_fora and not menciona_dentro:
            return f"Há {fora} pessoas fora do evento."

        if menciona_dentro and not menciona_fora:
            return f"Há {dentro} pessoas presentes no evento."

        return (
            f"Há {total} pessoas cadastradas no total: "
            f"{dentro} dentro e {fora} fora do evento."
        )

    # 6. Pergunta não reconhecida
    return (
        "Ainda não consegui interpretar essa pergunta. "
        "Experimente perguntar sobre quantidade, presença, "
        "situação, idade ou código de ingresso."
    )
