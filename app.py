
import streamlit as st
import pandas as pd

from chatbot import perguntar

from database import (
    listar_ingressos,
    buscar_ingresso,
    resumir_situacoes,
    incluir_ingresso,
    alterar_ingresso,
    excluir_ingresso,
)

st.set_page_config(
    page_title="Event Control",
    page_icon="🎟️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Personalização visual
st.markdown("""
<style>
    .stApp {
        background-color: #0b1020;
        color: #f1f5f9;
    }

    [data-testid="stSidebar"] {
        background-color: #121a2d;
        border-right: 1px solid #293650;
    }

    [data-testid="stMetric"] {
        background-color: #151f35;
        padding: 18px;
        border: 1px solid #293650;
        border-radius: 14px;
    }

    [data-testid="stMetricLabel"] {
        color: #a8b6d1;
    }

    [data-testid="stMetricValue"] {
        color: #f8fafc;
    }

    .hero {
        padding: 24px;
        border-radius: 18px;
        background: linear-gradient(120deg, #172554, #312e81, #164e63);
        border: 1px solid #394c83;
        margin-bottom: 22px;
    }

    .hero h1 {
        color: white;
        margin-bottom: 6px;
    }

    .hero p {
        color: #dbeafe;
        margin-bottom: 0;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        border-radius: 9px;
        font-weight: 600;
    }

    div[data-testid="stProgressBar"] > div > div {
        background-color: #22c55e;
    }
</style>
""", unsafe_allow_html=True)


# Navegação lateral
with st.sidebar:
    st.title("🎟️ Event Control")
    st.caption("Painel de gerenciamento")
    st.divider()

    pagina = st.radio(
        "MENU",
        [
            "🏠 Visão geral",
            "🔎 Consultar",
            "➕ Cadastrar",
            "🔄 Alterar status",
            "🗑️ Excluir",
            "🤖 Chatbot",
        ],
        label_visibility="visible",
    )

    st.divider()
    st.caption("Event Control • SQLite")


# Dados atuais do banco
resumo = resumir_situacoes() or {}
dentro = resumo.get("dentro", 0)
fora = resumo.get("fora", 0)
total = dentro + fora

# Capacidade configurada do evento
CAPACIDADE = 100
vagas = max(CAPACIDADE - dentro, 0)
ocupacao = dentro / CAPACIDADE if CAPACIDADE > 0 else 0


# VISÃO GERAL
if pagina == "🏠 Visão geral":
    st.markdown("""
    <div class="hero">
        <h1>Visão geral do evento</h1>
        <p>Acompanhe a entrada de participantes em tempo real.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🎟️ Ingressos", total)
    c2.metric("🟢 Dentro", dentro)
    c3.metric("🟠 Fora", fora)
    c4.metric("🪑 Vagas restantes", vagas)

    st.divider()

    esquerda, direita = st.columns([1.2, 1])

    with esquerda:
        st.subheader("📊 Situação dos ingressos")

        grafico = pd.DataFrame(
            {"Quantidade": [dentro, fora]},
            index=["Dentro", "Fora"],
        )

        st.bar_chart(
            grafico,
            color="#38bdf8",
            height=280,
        )

        st.caption(
            "O gráfico representa a situação atual dos ingressos cadastrados."
        )

    with direita:
        st.subheader("🏟️ Ocupação do evento")

        st.metric("Capacidade configurada", CAPACIDADE)
        st.progress(min(max(ocupacao, 0.0), 1.0))
        st.write(f"**{ocupacao:.1%}** da capacidade ocupada")

        if dentro >= CAPACIDADE:
            st.error("Capacidade atingida!")
        elif ocupacao >= 0.8:
            st.warning("Atenção: evento próximo da lotação.")
        else:
            st.success("Ocupação dentro do limite configurado.")

        st.info(
            "A capacidade está configurada para 100 pessoas. "
            "Altere CAPACIDADE no código para usar o limite do seu evento."
        )

    st.divider()
    st.subheader("🕒 Últimos ingressos cadastrados")

    ingressos = listar_ingressos()

    if ingressos:
        df = pd.DataFrame(
            ingressos,
            columns=["Código", "Idade", "Situação"],
        )

        st.dataframe(
            df.head(5),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Nenhum ingresso cadastrado.")


# CONSULTAR
elif pagina == "🔎 Consultar":
    st.title("🔎 Consultar ingresso")
    codigo = st.text_input("Código do ingresso")

    if st.button("Buscar", type="primary"):
        if not codigo.strip():
            st.warning("Digite um código.")
        else:
            ingresso = buscar_ingresso(codigo.strip())

            if ingresso:
                st.success("Ingresso encontrado")

                a, b, c = st.columns(3)
                a.metric("Código", ingresso[0])
                b.metric("Idade", ingresso[1])
                c.metric("Situação", ingresso[2].upper())
            else:
                st.error("Ingresso não encontrado.")

    st.subheader("Todos os ingressos")
    ingressos = listar_ingressos()

    st.dataframe(
        pd.DataFrame(
            ingressos,
            columns=["Código", "Idade", "Situação"],
        ),
        use_container_width=True,
        hide_index=True,
    )


# CADASTRAR
elif pagina == "➕ Cadastrar":
    st.title("➕ Cadastrar ingresso")
    st.write("Adicione um participante ao banco de dados.")

    with st.form("form_cadastro"):
        codigo = st.text_input("Código do ingresso")
        idade = st.number_input(
            "Idade",
            min_value=0,
            max_value=120,
            value=18,
        )
        situacao = st.selectbox(
            "Situação inicial",
            ["fora", "dentro"],
        )

        enviar = st.form_submit_button(
            "Cadastrar ingresso",
            type="primary",
        )

    if enviar:
        if not codigo.strip():
            st.warning("Digite o código do ingresso.")
        else:
            try:
                incluir_ingresso(codigo.strip(), int(idade), situacao)
                st.success("Ingresso cadastrado!")
                st.rerun()
            except Exception as erro:
                st.error(f"Não foi possível cadastrar: {erro}")


# ALTERAR STATUS
elif pagina == "🔄 Alterar status":
    st.title("🔄 Alterar situação")
    st.write("Registre a entrada ou a saída de um participante.")

    with st.form("form_alterar"):
        codigo = st.text_input("Código do ingresso")
        situacao = st.selectbox(
            "Nova situação",
            ["dentro", "fora"],
        )

        enviar = st.form_submit_button(
            "Atualizar situação",
            type="primary",
        )

    if enviar:
        if not codigo.strip():
            st.warning("Digite o código do ingresso.")
        else:
            try:
                alterar_ingresso(
                    codigo.strip(),
                    situacao=situacao,
                )
                st.success("Situação atualizada!")
                st.rerun()
            except Exception as erro:
                st.error(f"Não foi possível alterar: {erro}")


# EXCLUIR
elif pagina == "🗑️ Excluir":
    st.title("🗑️ Excluir ingresso")
    st.warning("A exclusão é permanente no banco de dados.")

    with st.form("form_excluir"):
        codigo = st.text_input("Código do ingresso")
        confirmar = st.checkbox(
            "Confirmo a exclusão deste ingresso."
        )

        enviar = st.form_submit_button("Excluir ingresso")

    if enviar:
        if not codigo.strip():
            st.warning("Digite o código do ingresso.")
        elif not confirmar:
            st.warning("Confirme a exclusão antes de continuar.")
        else:
            try:
                excluir_ingresso(codigo.strip())
                st.success("Ingresso excluído.")
                st.rerun()
            except Exception as erro:
                st.error(f"Não foi possível excluir: {erro}")


# CHATBOT
elif pagina == "🤖 Chatbot":
    st.title("🤖 Assistente Event Control")
    st.write(
        "Faça perguntas sobre os ingressos e a situação atual do evento."
    )

    if "historico_chat" not in st.session_state:
        st.session_state.historico_chat = []

    if st.button("Limpar conversa"):
        st.session_state.historico_chat = []
        st.rerun()

    for mensagem in st.session_state.historico_chat:
        with st.chat_message(mensagem["role"]):
            st.markdown(mensagem["content"])

    pergunta = st.chat_input("Pergunte sobre os ingressos...")

    if pergunta:
        st.session_state.historico_chat.append({
            "role": "user",
            "content": pergunta,
        })

        with st.chat_message("user"):
            st.markdown(pergunta)

        with st.chat_message("assistant"):
            with st.spinner("Consultando o Event Control..."):
                try:
                    resposta = perguntar(pergunta)
                except Exception as erro:
                    resposta = (
                        "Não consegui consultar o assistente agora. "
                        "Verifique o erro técnico abaixo."
                    )
                    st.error(resposta)

                    with st.expander("Detalhes técnicos"):
                        st.code(str(erro))
                else:
                    st.markdown(resposta)

        st.session_state.historico_chat.append({
            "role": "assistant",
            "content": resposta,
        })
