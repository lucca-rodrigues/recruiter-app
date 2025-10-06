"""Streamlit interface for the recruiter pipeline."""

from __future__ import annotations

import uuid
from typing import List

import streamlit as st

from src.modules.pipeline.pipeline_service import PipelineCreate, PipelineService

st.set_page_config(page_title="Recruiter Assistant", page_icon="🧑‍💼", layout="wide")

st.title("Assistente de Recrutamento")
st.write(
    "Carregue currículos (PDF ou imagem), informe quem está usando a ferramenta e, se quiser, "
    "faça uma pergunta para o assistente. O resultado usa OCR + LLM em tempo real."
)

if "pipeline_service" not in st.session_state:
    st.session_state.pipeline_service = PipelineService()

with st.form("pipeline_form"):
    col1, col2 = st.columns(2)
    with col1:
        request_id = st.text_input("request_id", value=str(uuid.uuid4()))
    with col2:
        user_id = st.text_input("user_id", value=str(uuid.uuid4()))

    query = st.text_area(
        "Pergunta (opcional)",
        help="Ex.: Qual desses currículos se encaixa melhor na vaga X?",
    )

    uploaded_files = st.file_uploader(
        "Currículos (PDF, PNG, JPG)",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )

    submitted = st.form_submit_button("Processar")

if submitted:
    if not uploaded_files:
        st.warning("Envie pelo menos um arquivo para processar.")
    elif not request_id or not user_id:
        st.warning("Preencha request_id e user_id.")
    else:
        with st.spinner("Processando documentos..."):
            file_inputs: List[tuple[bytes, str | None]] = []
            for file in uploaded_files:
                file_inputs.append((file.read(), file.name))

            service: PipelineService = st.session_state.pipeline_service
            payload = PipelineCreate(
                request_id=request_id,
                user_id=user_id,
                query=query.strip() if query else None,
                files=file_inputs,
            )
            try:
                response = service.create(payload)
            except Exception as exc:  # pragma: no cover - UI feedback
                st.error(f"Erro ao processar: {exc}")
            else:
                st.success("Processamento concluído!")

                if response.summaries:
                    st.subheader("Sumários por currículo")
                    for item in response.summaries:
                        st.markdown(f"### {item.filename or 'Documento sem nome'}")
                        st.write(item.summary)

                if response.answer:
                    st.subheader("Resposta à pergunta")
                    st.write(response.answer)

                with st.expander("Payload bruto"):
                    st.json(response.model_dump())
