from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph
import os
import neo4j
import time

# ENV = os.getenv('ENV', 'prod')
ENV = os.getenv('ENV', 'dev')
print(f'ENV: {ENV}')
# Load environment variables
if ENV == 'dev':
    load_dotenv('.env', override=True)
elif ENV == 'prod':
    load_dotenv('.env.aura', override=True)

# Database configuration
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
NEO4J_DATABASE = os.getenv('NEO4J_DATABASE') or 'neo4j'

class RetryNeo4jGraph(Neo4jGraph):
    def query(self, query, params=None, max_retries=5, retry_delay=5):
        attempt = 0
        while attempt < max_retries:
            try:
                return super().query(query, params)
            except (neo4j.exceptions.ServiceUnavailable, neo4j.exceptions.ClientError) as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                time.sleep(retry_delay)
                attempt += 1
        raise Exception("Query failed after several retries")

def init_kg() -> Neo4jGraph:
    return RetryNeo4jGraph(
        url=NEO4J_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
        database=NEO4J_DATABASE
    )

# kg = init_kg()

def paper_exists(arxiv_id):
    check_query = """
    MATCH (p:Paper {arxiv_id: $arxiv_id})
    OPTIONAL MATCH (p)-[:REFERENCES]->(ref)
    RETURN p, COUNT(ref) > 0 AS has_references
    """
    kg = init_kg()
    result = kg.query(check_query, params={'arxiv_id': arxiv_id})
    if result:
        paper_exists = result[0]['p'] is not None
        has_references = result[0]['has_references']
        if paper_exists and not has_references:
            print(f"Paper {arxiv_id} exists but has no references.")
        elif paper_exists and has_references:
            print(f"Paper {arxiv_id} exists and has references.")
        return paper_exists and has_references
    
    return False
