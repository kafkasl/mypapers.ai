from ariadne import QueryType, make_executable_schema, graphql_sync, load_schema_from_path
from flask import jsonify, request
from knowledge_graph.db import init_kg
import json 
type_defs = load_schema_from_path("schema.graphql")
query = QueryType()

def process_paper_record(paper, references=None, incomingReferencesCount=None):
    """Process a single paper record to standardize its structure."""
    if references is None:
        references = []
    if incomingReferencesCount is None:
        incomingReferencesCount = 0

    paper_node = {
        "id": paper['arxiv_id'],
        "title": paper['title'],
        "publicationDate": paper['published'],
        "summary": paper['summary'],
        "authors": paper['authors'],
        "source": paper['source'],
        "references": [ref['arxiv_id'] for ref in references], 
        "incomingReferencesCount": incomingReferencesCount
    }
    return paper_node

def process_query_results(results):
    papers_dict = {}

    for record in results:
        # Process main paper with its references and incoming references count
        paper_node = process_paper_record(
            record['paper'],
            record['references'],
            record['incomingReferencesCount'])

        # Always overwrite the paper node because it is always richer
        papers_dict[paper_node['id']] = paper_node

        # Process each reference and add to dictionary, avoiding duplicates
        for ref in record['references']:
            ref_node = process_paper_record(ref)
            # Only add if not already present to avoid overwriting richer data
            if ref_node['id'] not in papers_dict:
                papers_dict[ref_node['id']] = ref_node

    return {"papers": list(papers_dict.values())}

@query.field("getAllData")
def resolve_get_all_data(*_):
    kg = init_kg()
    cypher = """
    MATCH (p:Paper)
    OPTIONAL MATCH (ref:Paper)-[:REFERENCES]->(p)
    WITH p, COUNT(ref) AS incomingReferencesCount
    OPTIONAL MATCH (p)-[:REFERENCES]->(outRef:Paper)
    RETURN p AS paper, collect(outRef) AS references, incomingReferencesCount
    """
    results = kg.query(cypher)
    return process_query_results(results)

@query.field("getPapersByDate")
def resolve_get_papers_by_date(_, info, date='20240425'):
    print('Resolving papers by date', date)
    kg = init_kg()
    cypher = f"""
    MATCH (p:Paper)
    MATCH (ref:Paper  {{published: '{date}'}})-[:REFERENCES]->(p)
    WITH p, COUNT(ref) AS incomingReferencesCount
    OPTIONAL MATCH (p)-[:REFERENCES]->(outRef:Paper)
    RETURN p AS paper, collect(outRef) AS references, incomingReferencesCount
    """
    print('Cypher query:', cypher)
    results = kg.query(cypher)
    # print('Results:', results)
    return process_query_results(results)

# Create executable schema
schema = make_executable_schema(type_defs, query)

# Function to handle GraphQL requests
def handle_graphql_request():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request)
    status_code = 200 if success else 400
    return jsonify(result), status_code
