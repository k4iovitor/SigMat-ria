import json
import os

def transformar_json_em_chunks(caminho: str):
    with open(caminho, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    chunks = []

    for semestre, disciplinas in dados.items():
        for disciplina in disciplinas:
            nome_disciplina = disciplina.get("nome_bruto", "").strip()
            ementa = disciplina.get("ementa", "").strip()

            if not nome_disciplina:
                continue

            texto_chunk = f"Contexto: {semestre.capitalize()}\nDisciplina: {nome_disciplina}\nEmenta: {ementa}"

            chunk_obj = {
                "conteudo_texto": texto_chunk,
                "metadados": {
                    "semestre": semestre,
                    "nome_disciplina": nome_disciplina
                }
            }

            chunks.append(chunk_obj)
    
    return chunks

def main():
    doc_json = ["dados_curriculos_com_ementa/grade_curso_1626669.json", 
                "dados_curriculos_com_ementa/grade_curso_1626865.json", 
                "dados_curriculos_com_ementa/grade_curso_14289031.json", 
                "dados_curriculos_com_ementa/grade_curso_44146190.json"]
    
    pasta_destino = "chunks_processados" 
    os.makedirs(pasta_destino, exist_ok=True)

    for num_doc, documento in enumerate(doc_json):
        chunks = transformar_json_em_chunks(documento)

        for i, chunk in enumerate(chunks):
            print(f"---Chunk {i+1}---")
            print(chunk['conteudo_texto'])
            print("=" * 20)
        
        nome_ficheiro = f"chunks_curso_{num_doc + 1}.json"
        caminho_completo = os.path.join(pasta_destino, nome_ficheiro)
        
        with open(caminho_completo, "w", encoding="utf-8") as f_out:
            json.dump(chunks, f_out, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()