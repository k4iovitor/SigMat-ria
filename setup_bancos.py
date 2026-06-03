import os
import json
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Caminhos absolutos baseados na localização deste arquivo
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))  # pasta 'agente'
RAIZ_PROJETO = os.path.dirname(DIRETORIO_ATUAL)

# Carrega .env da raiz do projeto (funciona independente do CWD)
load_dotenv(os.path.join(RAIZ_PROJETO, ".env"))
chave_api = os.getenv("MINHA_CHAVE")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-2",
    api_key=chave_api
)

arquivos_cursos = [
    "chunks_curso_1.json",
    "chunks_curso_2.json",
    "chunks_curso_3.json",
    "chunks_curso_4.json"
]


def criar_banco():

    pasta_bancos = os.path.join(DIRETORIO_ATUAL, "bancos_vetoriais")
    os.makedirs(pasta_bancos, exist_ok=True)

    for arquivo_nome in arquivos_cursos:

        caminho_json = os.path.join(RAIZ_PROJETO, "chunks_processados", arquivo_nome)

        nome_base = os.path.basename(arquivo_nome)
        curso_id = nome_base.replace("chunks_", "").replace(".json", "")

        # Usa caminho absoluto consistente com gerenciador_agentes.py
        diretorio_persist = os.path.join(pasta_bancos, curso_id)

        if not os.path.exists(caminho_json):
            print(f"Erro: O arquivo não foi encontrado no caminho: {caminho_json}")
            continue

        with open(caminho_json, "r", encoding="utf-8") as f:
            dados_json = json.load(f)

        documentos = []

        for item in dados_json:
            doc = Document(
                page_content=item["conteudo_texto"],
                metadata=item["metadados"]
            )

            documentos.append(doc)
        
        Chroma.from_documents(
            documents=documentos,
            embedding=embeddings,
            persist_directory=diretorio_persist
        )
        print(f"Banco vetorial criado para {curso_id} em: {diretorio_persist}")


if __name__ == "__main__":
    criar_banco()
