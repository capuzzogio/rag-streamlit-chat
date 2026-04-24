import streamlit as st
import requests

API_URL = "https://capuzzogio-rag-pipeline.hf.space/ask"

# -----------------------------
# ⚙️ CONFIG
# -----------------------------
st.set_page_config(
    page_title="RAG Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Assistente Inteligente com RAG")

# -----------------------------
# 💾 HISTÓRICO
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# 💬 INPUT
# -----------------------------
user_input = st.chat_input("Digite sua pergunta...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Buscando conhecimento... 🤔"):

            try:
                response = requests.post(
                    API_URL,
                    json={"question": user_input},
                    timeout=60
                )

                data = response.json()

                results = data.get("results", [])
                answer = data.get("answer")

                # -----------------------------
                # 🧠 VALIDAÇÃO REAL DA RESPOSTA
                # -----------------------------
                if not answer or not answer.strip():
                    answer = "Não encontrei uma resposta gerada pelo modelo."

                # -----------------------------
                # 📚 FONTES
                # -----------------------------
                sources = []
                for r in results:
                    sources.append({
                        "titulo": r.get("titulo"),
                        "sistema": r.get("sistema", []),
                        "caminho": r.get("caminho_sistema")
                    })

            except Exception as e:
                answer = f"Erro ao conectar na API: {str(e)}"
                sources = []

        # -----------------------------
        # 💡 RESPOSTA
        # -----------------------------
        st.markdown("### 💡 Resposta")
        st.markdown(answer)

        # -----------------------------
        # 📚 FONTES
        # -----------------------------
        if sources:
            st.markdown("### 📚 Fontes encontradas")

            for s in sources:
                st.markdown(f"""
**📄 {s['titulo']}**  
🧠 Sistema: {', '.join(s.get('sistema', []))}  
📍 Caminho: {s.get('caminho')}
""")

    # salva histórico
    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

# -----------------------------
# 🧹 LIMPAR CHAT
# -----------------------------
if st.button("🧹 Limpar conversa"):
    st.session_state.messages = []