import json
import time
from knowledge_graph.db import init_kg

kg = init_kg()

def create_paper_from_file(file):
    with open(file, 'r') as f:
        data = json.load(f)
        paper_info = {
            'arxiv_id': data['id'],
            'title': data['title'],
            'source': data.get('source', ''),
            'text': ' '.join(data['summary']) if isinstance(data['summary'], list) else data['summary'],
            'authors': data['authors'],
            'categories': data['categories'],
            'published': data['published'],
            'updated': data['updated']
        }
        create_paper_node(paper_info)

def create_paper_node(paper_info):
    cypher = """
        MERGE (p:Paper {arxiv_id: $paperInfoParam.arxiv_id })
        ON CREATE SET
            p.title = $paperInfoParam.title,
            p.source = $paperInfoParam.source,
            p.summary = $paperInfoParam.text,
            p.authors = $paperInfoParam.authors,
            p.categories = $paperInfoParam.categories,
            p.published = $paperInfoParam.published,
            p.updated = $paperInfoParam.updated
    """
    kg.query(cypher, params={'paperInfoParam': paper_info})

def create_paper_nodes(files):
    start_time = time.time()
    for file in files:
        create_paper_from_file(file)
    total_time = time.time() - start_time
    print(f"Total time to create paper nodes: {total_time:.2f} seconds")

if __name__ == "__main__":
    files = [
        "./papers/AlphaStar Unplugged Large-Scale Offline Reinforcement Learning-2308.03526.json",
        "./papers/Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm-1712.01815.json"
    ]
    create_paper_nodes(files)
