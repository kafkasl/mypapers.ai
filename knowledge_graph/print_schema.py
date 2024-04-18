from knowledge_graph.db import init_kg


kg = init_kg()

print(kg.schema)

# Node properties are the following:
# Chunk {categories: LIST, textEmbedding: LIST, source: STRING, published: STRING, updated: STRING, chunk_seq_id: INTEGER, arxiv_id: STRING, authors: LIST, text: STRING, title: STRING, content_type: STRING, chunkId: STRING},Paper {title: STRING, source: STRING, published: STRING, updated: STRING, arxiv_id: STRING, authors: LIST, categories: LIST},Author {name: STRING}
# Relationship properties are the following:

# The relationships are the following:
# (:Chunk)-[:SUMMARY_OF]->(:Paper),(:Chunk)-[:AUTHORS_OF]->(:Paper),(:Chunk)-[:NEXT]->(:Chunk),(:Chunk)-[:PART_OF]->(:Paper),(:Paper)-[:CONTENT]->(:Chunk),(:Author)-[:AUTHOR_OF]->(:Paper)