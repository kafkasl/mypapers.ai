from ariadne import QueryType, make_executable_schema, graphql_sync, load_schema_from_path
from flask import jsonify, request
from knowledge_graph.db import init_kg

type_defs = load_schema_from_path("schema.graphql")
query = QueryType()

@query.field("getAllData")
def resolve_get_all_data(*_):
    kg = init_kg()
    cypher = """
            MATCH (a:Author)-[r:AUTHOR_OF]->(p:Paper)
            RETURN p AS paper, r AS link, a AS author
            """
    results = kg.query(cypher)
    authors = []
    papers = []
    links = []
    seen_authors = set()
    seen_papers = set()

    for record in results:
        paper = record['paper']
        link = record['link']
        author = record['author']

        if paper['arxiv_id'] not in seen_papers:
            paper_node = {
                "id": paper['arxiv_id'],
                "title": paper['title'],
                "type": "paper",
                "publicationDate": paper['published'],
                "summary": paper['summary'] if 'summary' in paper else "",
                "link": paper['source']
            }
            papers.append(paper_node)
            seen_papers.add(paper['arxiv_id'])

        if author['name'] not in seen_authors:
            author_node = {
                "id": author['name'],
                "name": author['name'],
                "type": "author"
            }
            authors.append(author_node)
            seen_authors.add(author['name'])

        links.append({
            "source": author['name'],
            "target": paper['arxiv_id'],
            "type": "author_of",
        })

    return {"papers": papers, "authors": authors, "links": links}


# Create executable schema
schema = make_executable_schema(type_defs, query)

# Function to handle GraphQL requests
def handle_graphql_request():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request)
    status_code = 200 if success else 400
    return jsonify(result), status_code
