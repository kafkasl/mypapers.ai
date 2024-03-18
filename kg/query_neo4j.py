from dotenv import load_dotenv
import os
import json
import textwrap
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_openai import ChatOpenAI
import warnings
warnings.filterwarnings("ignore")

load_dotenv('.env', override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VECTOR_INDEX_NAME = 'paper_chunks'
VECTOR_NODE_LABEL = 'Chunk'
VECTOR_SOURCE_PROPERTY = 'text'
VECTOR_EMBEDDING_PROPERTY = 'textEmbedding'

kg = Neo4jGraph(
    url=os.getenv("NEO4J_URI"), username=os.getenv("NEO4J_USERNAME"), password=os.getenv("NEO4J_PASSWORD"), database=os.getenv("NEO4J_DATABASE")
)

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

query = """
    In the AlphaStar paper, they don't introduce any new RL agent themselves? In addition to the benchmark?
"""

query = """Explain AlphaGo in one line.""" # OK
query = """Explain AlphaStar in one line.""" # OK
query = """Explain the differences between AlphaStar and AlphaGo in one line.""" # Explain differences completely fails

query += "If you are unsure about the answer, say you don't know."

# Use this to debug which chunks are retrieved
# search_results = neo4j_vector_search(query)
# print(search_results)


retriever = neo4j_vector_store.as_retriever()

chain = RetrievalQAWithSourcesChain.from_chain_type(
    ChatOpenAI(temperature=0, model="gpt-4"),
    chain_type="stuff",
    retriever=retriever
)

def prettychain(question: str) -> str:
    """Pretty print the chain's response to a question"""
    response = chain({"question": question},
        return_only_outputs=True,)
    print(response['answer'])
    print(response['sources'])

prettychain(query)
