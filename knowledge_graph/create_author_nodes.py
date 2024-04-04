
from dotenv import load_dotenv
import os

from knowledge_graph.neo4j_config import init_kg

load_dotenv('.env', override=True)

kg = init_kg()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VECTOR_INDEX_NAME = 'paper_chunks'
VECTOR_NODE_LABEL = 'Chunk'
VECTOR_SOURCE_PROPERTY = 'text'
VECTOR_EMBEDDING_PROPERTY = 'textEmbedding'

def create_author_nodes():
    # Execute the query to get authors along with a unique identifier for the paper (e.g., arxiv_id)
    authors_query = """
    MATCH (p:Paper)
    RETURN p.authors AS authors, p.arxiv_id AS arxiv_id
    """
    results = kg.query(authors_query)

    # Iterate over the results
    for result in results:
        authors_list = result['authors']
        paper_arxiv_id = result['arxiv_id']
        for author_name in authors_list:
            # For each author, check if an Author node already exists, create one if not,
            # and then create a relationship to the paper
            create_author_and_relationship_cypher = """
            MERGE (a:Author {name: $author_name})
            WITH a
            MATCH (p:Paper {arxiv_id: $paper_arxiv_id})
            MERGE (a)-[:AUTHOR_OF]->(p)
            """
            kg.query(create_author_and_relationship_cypher,
                     params={'author_name': author_name, 'paper_arxiv_id': paper_arxiv_id})


    # create full text index so we can search authors by similar name
    kg.query("""
    CREATE FULLTEXT INDEX fullTextAuthorNames
    IF NOT EXISTS
    FOR (a:Author)
    ON EACH [a.name]
    """)

if __name__ == '__main__':
    create_author_nodes()