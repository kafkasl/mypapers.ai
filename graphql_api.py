from ariadne import QueryType, make_executable_schema, graphql_sync, load_schema_from_path
from flask import jsonify, request
from knowledge_graph.db import init_kg

type_defs = load_schema_from_path("schema.graphql")
query = QueryType()

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
    papers = []
    authors = set()
    links = []

    for record in results:
        paper = record['paper']
        paper_node = {
            "id": paper['arxiv_id'],
            "title": paper['title'],
            "publicationDate": paper['published'],
            "summary": paper['summary'],
            "authors": paper['authors'],
            "references": [ref['arxiv_id'] for ref in record['references']],
            "incomingReferencesCount": record['incomingReferencesCount'],
            "source": paper['source']
        }
        papers.append(paper_node)
        authors.update(paper_node['authors'])
        links.extend([{"source": author, "target": paper_node['id'], "type": "author_of"} for author in paper_node['authors']])
        links.extend([{"source": paper_node['id'], "target": ref, "type": "references"} for ref in paper_node['references']])

    authors = [{"id": a, "name": a} for a in authors]
    return {"papers": papers, "authors": authors, "links": links}


# Create executable schema
schema = make_executable_schema(type_defs, query)

# Function to handle GraphQL requests
def handle_graphql_request():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request)
    status_code = 200 if success else 400
    return jsonify(result), status_code
