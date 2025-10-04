from fastapi import FastAPI

from src.modules.logs.log_controller import router as log_router
from src.modules.pipeline.pipeline_controller import router as pipeline_router

tags_metadata = [
    {
        "name": "Pipeline",
        "description": "Processamento completo de currículos: upload, OCR, uso de LLM e registro de logs.",
    },
    {
        "name": "Logs",
        "description": "Consulta e manutenção dos logs de uso registrados no MongoDB.",
    },
]

app = FastAPI(
    title="API Recruiter App",
    description=(
        "API responsável por receber currículos em PDF/imagem, executar OCR, gerar resumos,"
        " responder perguntas via LLM e registrar logs de uso para auditoria."
    ),
    version="1.0.0",
    openapi_tags=tags_metadata,
)

app.include_router(pipeline_router, prefix="/api")
app.include_router(log_router, prefix="/api")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Api is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
