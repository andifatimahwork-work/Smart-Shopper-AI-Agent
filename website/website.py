import asyncio
from uuid import uuid4

import streamlit as st

from smartshopper_agent.runtime import run_agent


def run_async(coro):
    return asyncio.run(coro)


st.set_page_config(page_title="SmartShopper Assistant")
st.title("SmartShopper Assistant")
st.caption("Google ADK agent with Product Recommendation and Common Information tools")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Tanyakan produk, refund, pengiriman, pembayaran, atau cara pembelian"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("SmartShopper sedang memilih tool yang tepat..."):
            response = run_async(
                run_agent(
                    query=prompt,
                    user_id="streamlit_user",
                    session_id=st.session_state.session_id,
                )
            )
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
