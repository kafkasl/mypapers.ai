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

def clear_neo4j_db():
    clear_db_query = """
    MATCH (n)
    DETACH DELETE n
    """
    kg.query(clear_db_query)

# Call the function to clear the database
# clear_neo4j_db()

files = ["./papers/AlphaStar Unplugged Large-Scale Offline Reinforcement Learning-2308.03526.json",
         "./papers/Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm-1712.01815.json"]

first_file_name = files[0]

first_file_as_object = json.load(open(first_file_name))

content_text = first_file_as_object['content']

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 4000,
    chunk_overlap  = 1000,
    length_function = len,
    is_separator_regex = False,
)

content_text_chunks = text_splitter.split_text(content_text)

def split_data_from_file(file):
    chunks_with_metadata = []
    file_as_object = json.load(open(file))
    arxiv_id = file_as_object['id']
    for content_type in ['summary','authors','content']:
        item_text = file_as_object[content_type]
        if type(item_text) == list: item_text = ' '.join(item_text)
        item_text_chunks = text_splitter.split_text(item_text)
        chunk_seq_id = 0
        for chunk in item_text_chunks[:20]:
            chunks_with_metadata.append({
                'text': chunk,
                'content_type': content_type,
                'chunk_seq_id': chunk_seq_id,
                'arxiv_id': f'{arxiv_id}',
                'chunkId': f'{arxiv_id}-{content_type}-chunk{chunk_seq_id:04d}',
                'authors': file_as_object['authors'],
                'published': file_as_object['published'],
                'updated': file_as_object['updated'],
                'source': file_as_object['source'],
                'categories': file_as_object['categories'],
            })
            chunk_seq_id += 1
    return chunks_with_metadata

first_file_chunks = split_data_from_file(first_file_name)

merge_chunk_node_query = """
MERGE(mergedChunk:Chunk {chunkId: $chunkParam.chunkId})
    ON CREATE SET
        mergedChunk.text = $chunkParam.text,
        mergedChunk.content_type = $chunkParam.content_type,
        mergedChunk.chunk_seq_id = $chunkParam.chunk_seq_id,
        mergedChunk.arxiv_id = $chunkParam.arxiv_id,
        mergedChunk.authors = $chunkParam.authors,
        mergedChunk.published = $chunkParam.published,
        mergedChunk.updated = $chunkParam.updated,
        mergedChunk.source = $chunkParam.source,
        mergedChunk.categories = $chunkParam.categories
RETURN mergedChunk
"""



kg.query(merge_chunk_node_query,
         params={'chunkParam':first_file_chunks[0]})

kg.query("""
CREATE CONSTRAINT unique_chunk IF NOT EXISTS
    FOR (c:Chunk) REQUIRE c.chunkId IS UNIQUE
""")

node_count = 0
for chunk in first_file_chunks:
    kg.query(merge_chunk_node_query,
            params={
                'chunkParam': chunk
            })
    node_count += 1


kg.query("""
         CREATE VECTOR INDEX `paper_chunks` IF NOT EXISTS
          FOR (c:Chunk) ON (c.textEmbedding)
          OPTIONS { indexConfig: {
            `vector.dimensions`: 1536,
            `vector.similarity_function`: 'cosine'
         }}
""")

kg.query("""
    MATCH (chunk:Chunk) WHERE chunk.textEmbedding IS NULL
    WITH chunk, genai.vector.encode(
      chunk.text,
      "OpenAI",
      {
        token: $openAiApiKey
      }) AS vector
    CALL db.create.setNodeVectorProperty(chunk, "textEmbedding", vector)
    """,
    params={"openAiApiKey":OPENAI_API_KEY} )

kg.refresh_schema()
print(kg.schema)

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


search_results = neo4j_vector_search(
    'In a single sentence, tell me about AlphaStar.'
)


print(search_results[0])

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
    ChatOpenAI(temperature=0),
    chain_type="stuff",
    retriever=retriever
)

def prettychain(question: str) -> str:
    """Pretty print the chain's response to a question"""
    response = chain({"question": question},
        return_only_outputs=True,)
    print(textwrap.fill(response['answer'], 60))


question = "What is Netapp's primary business?"

prettychain(question)

prettychain("Where is Netapp headquartered?")

prettychain("""
    Tell me about Netapp.
    Limit your answer to a single sentence.
""")

prettychain("""
    Tell me about Apple.
    Limit your answer to a single sentence.
""")


prettychain("""
    Tell me about Apple.
    Limit your answer to a single sentence.
    If you are unsure about the answer, say you don't know.
""")

prettychain("""
    ADD YOUR OWN QUESTION HERE
""")
