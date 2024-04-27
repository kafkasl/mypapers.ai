from knowledge_graph.db import init_kg
import json

kg = init_kg()

def create_reference_edges(files, verbose=False):
    for file in files:
        with open(file, 'r') as f:
            data = json.load(f)
            paper_id = data['id']
            references = data.get('references', [])
            for ref in references:
                ref_id = ref['id']
                if ref_id == paper_id:
                    continue
                cypher = """
                MATCH (p1:Paper {arxiv_id: $paper_id}), (p2:Paper {arxiv_id: $ref_id})
                MERGE (p1)-[r:REFERENCES]->(p2)
                RETURN p1, p2, r
                """
                result = kg.query(cypher, params={'paper_id': paper_id, 'ref_id': ref_id})
                if not result and verbose:
                    print(f"not found {ref_id} [{paper_id}]")

if __name__ == "__main__":
    files = ["./papers/G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering-2402.07630.json"]
    create_reference_edges(files)