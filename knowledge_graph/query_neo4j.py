from dotenv import load_dotenv
import os
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_openai import ChatOpenAI
from knowledge_graph.db import init_kg
import warnings
warnings.filterwarnings('ignore')

load_dotenv('.env', override=True)


kg = init_kg()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VECTOR_INDEX_NAME = 'paper_chunks'
VECTOR_NODE_LABEL = 'Chunk'
VECTOR_SOURCE_PROPERTY = 'text'
VECTOR_EMBEDDING_PROPERTY = 'textEmbedding'


# retrieves source for a given question using embeddings & cosine similarity
def neo4j_vector_search(question: str) -> list:
  vector_search_query = """
    WITH genai.vector.encode(
      $question,
      "OpenAI",
      {
        token: $openAiApiKey
      }) AS question_embedding
    CALL db.index.vector.queryNodes($index_name, $top_k, question_embedding) yield node, score
    RETURN score, node.text AS text
  """
  similar = kg.query(vector_search_query,
                     params={
                      'question': question,
                      'openAiApiKey':OPENAI_API_KEY,
                      'index_name':VECTOR_INDEX_NAME,
                      'top_k': 10})
  return similar


neo4j_vector_store = Neo4jVector.from_existing_graph(
    embedding=OpenAIEmbeddings(),
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    index_name=VECTOR_INDEX_NAME,
    node_label=VECTOR_NODE_LABEL,
    text_node_properties=[VECTOR_SOURCE_PROPERTY],
    embedding_node_property=VECTOR_EMBEDDING_PROPERTY,
)


retriever = neo4j_vector_store.as_retriever()

chain = RetrievalQAWithSourcesChain.from_chain_type(
    ChatOpenAI(temperature=0, model="gpt-4"),
    chain_type="stuff",
    retriever=retriever
)

def question_with_simple_sources(question: str) -> str:
    """Pretty print the chain's response to a question"""
    response = chain({"question": question},
        return_only_outputs=False,)
    print(response['answer'])
    print(response['sources'])


# example of a query using a path
def question_path_of_chunks(chunk_id = "2308.03526-content-chunk0000"):
    # ### Information is stored in the structure of a graph
    # - Matched patterns of nodes and relationships in a graph are called **paths**
    # - The length of a path is equal to the number of relationships in the path
    # - Paths can be captured as variables and used elsewhere in queries

    chunk_id = "2308.03526-content-chunk0000"
    #- Modify `NEXT` relationship to have variable length
    # - Retrieve only the longest path
    cypher = """
    MATCH window=
        (:Chunk)-[:NEXT*0..1]->(c:Chunk)-[:NEXT*0..1]->(:Chunk)
        WHERE c.chunkId = $chunkIdParam
    WITH window as longestChunkWindow
        ORDER BY length(window) DESC LIMIT 1
    RETURN length(longestChunkWindow)
    """

    return kg.query(cypher,
            params={'chunkIdParam': chunk_id})


# example augmenting with extra text the retrieved results
def question_with_extra_text(question =  "What topics does Andreas know about?"):
    # ### Customize the results of the similarity search using Cypher
    # - Extend the vector store definition to accept a Cypher query
    # - The Cypher query takes the results of the vector similarity search and then modifies them in some way
    # - Start with a simple query that just returns some extra text along with the search results
    # - Set up the vector store to use the query, then instantiate a retriever and Question-Answer chain in LangChain
    # - Note, you'll need to reset the vector store, retriever, and chain each time you change the Cypher query.

    retrieval_query_extra_text = """
    WITH node, score, "Andreas knows Cypher. " as extraText
    RETURN extraText + "\n" + node.text as text,
        score,
        node {.source} AS metadata
    """
    vector_store_extra_text = Neo4jVector.from_existing_index(
        embedding=OpenAIEmbeddings(),
        url=NEO4J_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
        database="neo4j",
        index_name=VECTOR_INDEX_NAME,
        text_node_property=VECTOR_SOURCE_PROPERTY,
        retrieval_query=retrieval_query_extra_text,
    )

    # Create a retriever from the vector store
    retriever_extra_text = vector_store_extra_text.as_retriever()

    # Create a chatbot Question & Answer chain from the retriever
    chain_extra_text = RetrievalQAWithSourcesChain.from_chain_type(
        ChatOpenAI(temperature=0),
        chain_type="stuff",
        retriever=retriever_extra_text
    )

    return chain_extra_text(
        {"question": question},
        return_only_outputs=False)



# def prettychain(question: str) -> str:
#     """Pretty print the chain's response to a question and debug the retrieved sources."""
#     # Debugging: Perform the vector search to see which sources are retrieved
#     search_results = neo4j_vector_search(question)
#     print("Debugging - Search Results:")
#     for r in search_results:
#         print(f"Score: {r['score']}, Text: {r['text']}")

#     # Generate the response using the chain
#     response = chain({"question": question},
#                      return_only_outputs=True,)
#     print("Response:")
#     print(response['answer'])
#     print("Sources:")
#     print(response['sources'])



query = """
    In the AlphaStar paper, they don't introduce any new RL agent themselves? In addition to the benchmark?
"""

query = """Explain AlphaGo in one line.""" # OK
query = """Explain AlphaStar in one line.""" # OK
query = """Explain the differences between AlphaStar and AlphaZero.""" # Explain differences completely fails

query += "If you are unsure about the answer, say you don't know."

# Use this to debug which chunks are retrieved
# search_results = neo4j_vector_search(query)
# print(search_results)

