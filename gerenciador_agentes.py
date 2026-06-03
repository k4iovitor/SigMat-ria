import os
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Caminhos absolutos baseados na localização deste arquivo
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))  # pasta 'agente'
RAIZ_PROJETO = os.path.dirname(DIRETORIO_ATUAL)

# Carrega .env da raiz do projeto (funciona independente do CWD)
load_dotenv(os.path.join(RAIZ_PROJETO, ".env"))
chave_api = os.getenv("MINHA_CHAVE")

cadeias_por_curso = {}

# Mapeamento: ID real do SIGAA -> ID interno do banco vetorial
# A ordem segue chunks.py: grade_curso_1626669 → curso_1, grade_curso_1626865 → curso_2, etc.
MAPA_ID_CURSOS = {
    "1626669":  "curso_1",
    "1626865":  "curso_2",
    "14289031": "curso_3",
    "44146190": "curso_4",
}


def inicializar_todos_agentes():

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2",
        api_key=chave_api
    )

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        temperature=0.5,
        google_api_key=chave_api
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """Você é um especialista na área de tecnologia que tem como principal função orientar estudantes de uma Universidade.
O aluno informou o nome do curso dele e selecionou disciplinas específicas do currículo.
Com base no contexto fornecido (ementas e dados das disciplinas), explique de forma clara e objetiva qual é a função e a importância de cada disciplina selecionada para a formação na área do curso informado.
Se uma disciplina selecionada não estiver no contexto, informe que ela não foi encontrada no currículo disponível.

Contexto das disciplinas do currículo:
{context}"""),
            ("human", "{query}")
        ]
    )

    def formatar_doc(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    ids_dos_cursos = ["curso_1", "curso_2", "curso_3", "curso_4"]

    for curso_id in ids_dos_cursos:
        # Caminho absoluto baseado em __file__, não em CWD
        caminho_banco = os.path.join(DIRETORIO_ATUAL, "bancos_vetoriais", curso_id)

        if os.path.exists(caminho_banco):

            vectorstore = Chroma(persist_directory=caminho_banco, embedding_function=embeddings)
            retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

            cadeia = (
                {"context": retriever | formatar_doc, "query": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )
            cadeias_por_curso[curso_id] = cadeia
            print(f"Agente ativado para o {curso_id}.")
        else:
            print(f"Aviso: Banco do {curso_id} não encontrado em '{caminho_banco}'. Ele não estará disponível.")


def _resolver_curso_id(curso_id_recebido: str) -> str:
    """
    Traduz o ID recebido do frontend para o ID interno do banco vetorial.
    Aceita tanto o ID real do SIGAA (ex: '14289031') quanto o interno (ex: 'curso_1').
    """
    # Se já é um ID interno válido, usa direto
    if curso_id_recebido in cadeias_por_curso:
        return curso_id_recebido

    # Senão, tenta traduzir pelo mapa de IDs reais
    curso_interno = MAPA_ID_CURSOS.get(curso_id_recebido)
    if curso_interno and curso_interno in cadeias_por_curso:
        return curso_interno

    raise ValueError(
        f"O curso '{curso_id_recebido}' não foi reconhecido. "
        f"IDs válidos: {list(MAPA_ID_CURSOS.keys())} ou {list(cadeias_por_curso.keys())}"
    )


def processar_pergunta(curso_id: str, curso_nome: str, disciplinas: list[str]) -> str:
    """
    Recebe o ID do curso, o nome do curso e a lista de disciplinas selecionadas.
    Monta a query e envia para a chain correspondente.
    """
    curso_interno = _resolver_curso_id(curso_id)

    # Monta a query com base nas disciplinas selecionadas pelo aluno
    lista_disciplinas = "\n".join(f"- {d}" for d in disciplinas)
    query = (
        f"Meu curso é {curso_nome}. "
        f"Selecionei as seguintes disciplinas:\n{lista_disciplinas}\n\n"
        f"Explique a função e a importância de cada uma dessas disciplinas para a minha formação na área de {curso_nome}."
    )

    cadeia_especifica = cadeias_por_curso[curso_interno]
    return cadeia_especifica.invoke(query)