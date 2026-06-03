# SigMatéria — Portal do Estudante

O **SigMatéria** é uma aplicação Full-Stack inteligente desenvolvida para ajudar estudantes universitários a entenderem a função e a importância de cada disciplina em sua grade curricular.

O sistema automatiza a extração de dados acadêmicos do SIGAA da UFPB, processa essas informações criando um banco de dados vetorial e utiliza Inteligência Artificial (RAG com LangChain e Gemini) para explicar o propósito das matérias selecionadas de forma clara e objetiva.

<img width="1106" height="776" alt="Screenshot_2026-06-02_23-25-42" src="https://github.com/user-attachments/assets/66ac3c00-3d22-47a9-a5b1-b465d07c482f" />
*Interface do usuário estilizada, permitindo a seleção do curso e das disciplinas desejadas.*

---

## Arquitetura e Funcionalidades

O projeto é dividido em um pipeline de Engenharia de Dados/IA e uma aplicação web interativa:

* **Web Scraping Automático:** Utiliza Selenium (`acesso.py`) para navegar no SIGAA, abrir pop-ups detalhados e extrair as ementas e cargas horárias dos componentes curriculares.
* **Processamento de Dados (Chunking):** Transforma os currículos extraídos (em formato JSON) em blocos de texto estruturados contendo semestre, nome da disciplina e ementa (`chunks.py`).
* **Banco de Dados Vetorial:** Constrói coleções persistentes usando o ChromaDB e o modelo de embeddings `gemini-embedding-2` do Google (`setup_bancos.py`).
* **Agente Especialista (LLM):** Integra o modelo `gemini-2.5-flash` via LangChain para atuar como um orientador acadêmico, recuperando o contexto exato da disciplina na base vetorial para responder ao aluno (`gerenciador_agentes.py`).
* **API Backend:** Desenvolvida em FastAPI (`main.py`), gerenciando rotas de consulta (`/cursos`, `/disciplinas/{curso_id}`) e processamento de chat (`/chat`), além de servir o frontend estático.
* **Frontend Dinâmico:** Uma interface construída com HTML, CSS e JavaScript puros (`index.html`), com animações fluidas, texturas visuais de ruído e requisições assíncronas para a API.

---

## Fluxo de Uso no Frontend

### 1. Seleção de Curso e Disciplinas
O aluno acessa a página, escolhe seu curso e seleciona uma ou mais matérias que causam dúvida. A API retorna dinamicamente a lista de disciplinas disponíveis para aquele curso.

<img width="1106" height="790" alt="Screenshot_2026-06-02_23-26-00" src="https://github.com/user-attachments/assets/6f1b217b-6e4f-4930-ae1d-d272031d85f8" />

### 2. Geração da Resposta Contextualizada
Ao clicar em "Descobrir de uma vez", o agente recupera a ementa exata do banco vetorial e gera uma explicação contextualizada sobre o impacto da matéria na formação profissional.

<img width="1106" height="906" alt="Screenshot_2026-06-02_23-26-17" src="https://github.com/user-attachments/assets/026bd91e-d17f-49da-962b-c06c9ec9c08e" />
<img width="1106" height="906" alt="Screenshot_2026-06-02_23-26-24" src="https://github.com/user-attachments/assets/1b6a8975-bc33-4e5b-8f30-0ec139e64270" />
<img width="1106" height="906" alt="Screenshot_2026-06-02_23-26-35" src="https://github.com/user-attachments/assets/e43ff33f-4686-4535-bd45-753a817e3fa6" />

*Resposta gerada pelo agente LangChain baseada no currículo extraído, detalhando o porquê de cada matéria ser fundamental para a área escolhida.*

---

## Cursos Suportados

Atualmente, o sistema extrai e serve dados para os seguintes cursos:
* Ciência da Computação (ID: `1626669`)
* Engenharia da Computação (ID: `1626865`)
* Ciência de Dados e Inteligência Artificial (ID: `14289031`)
* Engenharia de Robôs (ID: `44146190`)

---

## Estrutura do Projeto

```text
projeto/
│
├──  acesso.py                  # Bot em Selenium que extrai ementas do SIGAA
├──  chunks.py                  # Formata o JSON bruto em chunks de texto estruturados
├──  setup_bancos.py            # Gera os embeddings e salva no ChromaDB
├──  gerenciador_agentes.py     # Configura o LangChain (Prompt, Retriever e LLM)
├──  main.py                    # Backend em FastAPI
│
├──  dados_curriculos_com_ementa/ # JSONs brutos gerados pelo scraper
├──  chunks_processados/        # JSONs estruturados para a IA
├──  bancos_vetoriais/          # Diretório de persistência do ChromaDB
│
└──  frontend/
    └──  index.html             # Interface web da aplicação SigMatéria
