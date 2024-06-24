from knowledge_graph.db import init_kg
import time

kg = init_kg()


def create_author_nodes():

    start_time = time.time()
    # kg.query("CREATE INDEX authorNameIndex IF NOT EXISTS FOR (a:Author) ON (a.name)")
    # kg.query("CREATE INDEX paperArxivIdIndex IF NOT EXISTS FOR (p:Paper) ON (p.arxiv_id)")

    # Execute the query to get authors along with a unique identifier for the paper (e.g., arxiv_id)
    authors_query = """
    MATCH (p:Paper)
    RETURN p.authors AS authors, p.arxiv_id AS arxiv_id
    """
    results = kg.query(authors_query)
    query_time = time.time() - start_time
    print(f"Time to execute authors query: {query_time:.2f} seconds")

    # Iterate over the results
    processing_start_time = time.time()
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
    processing_time = time.time() - processing_start_time
    print(f"Time to process results and update graph: {processing_time:.2f} seconds")

    # create full text index so we can search authors by similar name
    index_start_time = time.time()
    kg.query("""
    CREATE FULLTEXT INDEX fullTextAuthorNames
    IF NOT EXISTS
    FOR (a:Author)
    ON EACH [a.name]
    """)
    index_time = time.time() - index_start_time
    print(f"Time to create full text index: {index_time:.2f} seconds")

    total_time = time.time() - start_time
    print(f"Total execution time: {total_time:.2f} seconds")

if __name__ == '__main__':
    create_author_nodes()
