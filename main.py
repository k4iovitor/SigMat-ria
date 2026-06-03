import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from contextlib import asynccontextmanager
from gerenciador_agentes import inicializar_todos_agentes, processar_pergunta

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROJETO = os.path.dirname(DIRETORIO_ATUAL)
PASTA_FRONTEND = os.path.join(DIRETORIO_ATUAL, "frontend")

CURSOS_INFO = {
    "curso_1": {"nome": "Ciência da Computação",    "sigaa_id": "1626669"},
    "curso_2": {"nome": "Engenharia da Computação",  "sigaa_id": "1626865"},
    "curso_3": {"nome": "Ciência de Dados e IA",     "sigaa_id": "14289031"},
    "curso_4": {"nome": "Engenharia de Robôs",       "sigaa_id": "44146190"},
}

def _carregar_disciplinas(curso_id: str) -> list[str]:
    caminho = os.path.join(RAIZ_PROJETO, "chunks_processados", f"chunks_{curso_id}.json")
    if not os.path.exists(caminho):
        return []
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)
    
    vistos = set()
    nomes = []
    for item in dados:
        nome = item["metadados"]["nome_disciplina"]
        if nome not in vistos:
            vistos.add(nome)
            nomes.append(nome)
    return nomes

@asynccontextmanager
async def lifespan(app: FastAPI):
    inicializar_todos_agentes()
    yield

app = FastAPI(title="Portal do Estudante - Agentes de Cursos", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PerguntaAluno(BaseModel):
    curso_id: str
    curso_nome: str
    disciplinas: list[str]

class RespostaIA(BaseModel):
    resposta: str

class CursoInfo(BaseModel):
    id: str
    nome: str

class DisciplinasList(BaseModel):
    curso_id: str
    curso_nome: str
    disciplinas: list[str]

@app.get("/cursos", response_model=list[CursoInfo])
async def listar_cursos():
    return [
        CursoInfo(id=cid, nome=info["nome"])
        for cid, info in CURSOS_INFO.items()
    ]

@app.get("/disciplinas/{curso_id}", response_model=DisciplinasList)
async def listar_disciplinas(curso_id: str):
    if curso_id not in CURSOS_INFO:
        raise HTTPException(status_code=404, detail=f"Curso '{curso_id}' não encontrado.")
    
    info = CURSOS_INFO[curso_id]
    disciplinas = _carregar_disciplinas(curso_id)
    return DisciplinasList(
        curso_id=curso_id,
        curso_nome=info["nome"],
        disciplinas=disciplinas,
    )

@app.post("/chat", response_model=RespostaIA)
async def endpoint_chat(req: PerguntaAluno):
    try:
        if not req.disciplinas:
            raise HTTPException(status_code=400, detail="Nenhuma disciplina foi selecionada.")

        resposta_llm = processar_pergunta(req.curso_id, req.curso_nome, req.disciplinas)
        return RespostaIA(resposta=resposta_llm)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no processamento: {str(e)}")

@app.get("/")
async def servir_index():
    return FileResponse(os.path.join(PASTA_FRONTEND, "index.html"))

app.mount("/static", StaticFiles(directory=PASTA_FRONTEND), name="static")