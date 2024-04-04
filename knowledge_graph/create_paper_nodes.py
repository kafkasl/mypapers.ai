
from dotenv import load_dotenv
import os

# Common data processing
import textwrap

# Langchain
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

# Warning control
import warnings
warnings.filterwarnings("ignore")

load_dotenv('.env', override=True)
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
NEO4J_DATABASE = os.getenv('NEO4J_DATABASE') or 'neo4j'



OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VECTOR_INDEX_NAME = 'paper_chunks'
VECTOR_NODE_LABEL = 'Chunk'
VECTOR_SOURCE_PROPERTY = 'text'
VECTOR_EMBEDDING_PROPERTY = 'textEmbedding'

kg = Neo4jGraph(
    url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD, database=NEO4J_DATABASE
)

#===============================================
# Use distinct chunk info to get paper list
#===============================================
def get_list_of_papers():
    cypher = """
    MATCH (anyChunk:Chunk)
    WITH anyChunk
    RETURN DISTINCT anyChunk {
        .arxiv_id,
        .title,
        .source,
        .authors,
        .categories,
        .published,
        .updated
        } as paperInfo
    """
    paper_info_list = kg.query(cypher)

    return paper_info_list


# ===============================================
# Add a linked list between the chunks of content
# ===============================================
def create_next_edges(paper_info):
    #  Add a NEXT relationship between subsequent chunks
    # - Use the `apoc.nodes.link` function from Neo4j to link ordered list of `Chunk` nodes with a `NEXT` relationship
    # - Do this for just the "Item 1" section to start
    cypher = """
    MATCH (from_content:Chunk)
    WHERE from_content.arxiv_id = $arxiv_id_param
        AND from_content.content_type = $content_type
    WITH from_content
        ORDER BY from_content.chunk_seq_id ASC
    WITH collect(from_content) as content_chunk_list
        CALL apoc.nodes.link(
            content_chunk_list,
            "NEXT",
            {avoidDuplicates: true}
        )
    RETURN size(content_chunk_list)
    """

    kg.query(cypher, params={'arxiv_id_param': paper_info['arxiv_id'],
                            'content_type': 'content'})



def create_paper_node(paper_info):
    # create a new paper from the chunks
    cypher = """
        MERGE (p:Paper {arxiv_id: $paperInfoParam.arxiv_id })
        ON CREATE
            SET p.title = $paperInfoParam.title
            SET p.source = $paperInfoParam.source
            SET p.authors = $paperInfoParam.authors
            SET p.categories = $paperInfoParam.categories
            SET p.published = $paperInfoParam.published
            SET p.updated = $paperInfoParam.updated
    """

    kg.query(cypher, params={'paperInfoParam': paper_info})


def get_number_of_papers():
       # check how many paper nodes have been added
    kg.query("MATCH (p:Paper) RETURN count(p) as paperCount")

    # just checking the conents before doing stuff
    cypher = """
    MATCH (from_content:Chunk)
    WHERE from_content.arxiv_id = $arxiv_id_param
        AND from_content.content_type = $content_type
        WITH from_content {
        .arxiv_id,
        .title,
        .chunkId,
        .chunk_seq_id
        }
        ORDER BY from_content.chunk_seq_id ASC
        LIMIT 10
    RETURN collect(from_content)
    """

    # retrieving all content chunks (no summary or authors) for a given paper
    return kg.query(cypher, params={'arxiv_id_param': paper_info['arxiv_id'], 'content_type': 'content'})




# ===============================================
# Connect **content** chunks to the paper with a PART_OF relationship
# Connect **summary** chunks to the paper with a SUMMARY_OF relationship
# Connect **authors** chunks to the paper with a AUTHORS_OF relationship (DEPRECATED)
# Create a CONTENT relationship on first chunk of each paper
# ===============================================
def connect_chunks():
    cypher = """
    MATCH (c:Chunk), (p:Paper)
    WHERE c.arxiv_id = p.arxiv_id
    AND c.content_type = 'content'

    MERGE (c)-[newRelationship:PART_OF]->(p)
    RETURN count(newRelationship)
    """
    kg.query(cypher)

    cypher = """
    MATCH (c:Chunk), (p:Paper)
    WHERE c.arxiv_id = p.arxiv_id
    AND c.content_type = 'summary'

    MERGE (c)-[newRelationship:SUMMARY_OF]->(p)
    RETURN count(newRelationship)
    """
    kg.query(cypher)

    # No longer needed because we'll create individual author nodes
    #   cypher = """
    #   MATCH (c:Chunk), (p:Paper)
    #     WHERE c.arxiv_id = p.arxiv_id
    #     AND c.content_type = 'authors'

    #   MERGE (c)-[newRelationship:AUTHORS_OF]->(p)
    #   RETURN count(newRelationship)
    #   """
    #   kg.query(cypher)

    # Create a CONTENT relationship on first chunk of each paper
    cypher = """
        MATCH (first:Chunk {content_type: "content"}), (p:Paper)
        WHERE first.arxiv_id = p.arxiv_id
        AND first.chunk_seq_id = 0
        WITH first, p
        MERGE (p)-[r:CONTENT]->(first)
        RETURN count(r)
    """

    kg.query(cypher)

    # - Return a window of three chunks

    cypher = """
        MATCH (c1:Chunk)-[:NEXT]->(c2:Chunk)-[:NEXT]->(c3:Chunk)
        RETURN c1.chunkId, c2.chunkId, c3.chunkId
        """

    kg.query(cypher)

def create_paper_nodes():
    paper_info_list = get_list_of_papers()

    for item in paper_info_list:
        paper_info = item['paperInfo']
        create_next_edges(paper_info)
        create_paper_node(paper_info)

    kg.refresh_schema()
    print(kg.schema)

    # check how many paper nodes have been added
    r = get_number_of_papers()
    print(r)

    connect_chunks()

if __name__ == "__main__":
    create_paper_nodes()