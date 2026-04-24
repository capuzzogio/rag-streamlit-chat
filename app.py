import streamlit as st
import requests

API_URL = "https://capuzzogio-rag-pipeline.hf.space/ask"

st.markdown("""
<style>
.stChatMessage {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="RAG Assistant", page_icon="🤖", layout="centered")

st.title("🤖 Assistente Inteligente com RAG")

# histórico
if "messages" not in st.session_state:
    st.session_state.messages = []

# render histórico
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# input do usuário
user_input = st.chat_input("Digite sua pergunta...")

if user_input:
    # salva pergunta
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    answer = ""
    sources = []

    with st.chat_message("assistant"):
        with st.spinner("Buscando conhecimento... 🤔"):

            try:
                response = requests.post(
                    API_URL,
                    json={"question": user_input},
                    timeout=60
                )

                data = response.json()

                # -----------------------------
                # 🔥 EXTRAI RESPOSTA INTELIGENTE
                # -----------------------------
                results = data.get("results", [])

                answer = (
                    data.get("answer")
                    or data.get("response")
                    or data.get("result")
                )

                # fallback: usa primeiro resultado
                if not answer and results:
                    first = results[0]
                    answer = first.get("conteudo") or first.get("titulo")

                # -----------------------------
                # 📚 ORGANIZA FONTES
                # -----------------------------
                sources = []
                for r in results:
                    sources.append({
                        "titulo": r.get("titulo"),
                        "sistema": r.get("sistema", []),
                        "caminho": r.get("caminho_sistema")
                    })

                if not answer:
                    answer = "Não foi possível gerar uma resposta."

            except Exception as e:
                answer = f"Erro ao conectar na API: {str(e)}"

        # -----------------------------
        # 💡 RESPOSTA FORMATADA
        # -----------------------------
        st.markdown("### 💡 Resposta")
        st.write(answer)

        # -----------------------------
        # 📚 FONTES BONITAS
        # -----------------------------
        if sources:
            st.markdown("### 📚 Fontes encontradas")

            for s in sources:
                st.markdown(f"""
**📄 {s.get('titulo')}**  
🧠 Sistema: {', '.join(s.get('sistema', []))}  
📍 Caminho: {s.get('caminho')}
                """)

    # salva no histórico
    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

# -----------------------------
# 🧹 LIMPAR CHAT
# -----------------------------
if st.button("🧹 Limpar conversa"):
    st.session_state.messages = []