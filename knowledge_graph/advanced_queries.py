import textwrap

# Langchain
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import GraphCypherQAChain
from langchain_openai import ChatOpenAI
from knowledge_graph.db import init_kg
import warnings
warnings.filterwarnings('ignore')


kg = init_kg()


CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to
query a graph database.
Instructions:
Use only the provided relationship types and properties in the
schema. Do not use any other relationship types or properties that
are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than
for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Examples: Here are a few examples of generated Cypher
statements for particular questions:


# Which papers has Oriol Vinyals written?
CALL db.index.fulltext.queryNodes(
    "fullTextAuthorNames",
    "Oriol Vinals"
    ) YIELD node
WITH node as author
MATCH (author:Author)-[:AUTHOR_OF]->(p:Paper)
RETURN p.title

# Get summaries of papers' written by Oriol Vinyals
CALL db.index.fulltext.queryNodes(
    "fullTextAuthorNames",
    "Oriol Vinals"
    ) YIELD node
WITH node as author
MATCH (author:Author)-[:AUTHOR_OF]->(p:Paper)<-[:SUMMARY_OF]-(s:Chunk)
RETURN s.text

The question is:
{question}"""

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE
)

cypherChain = GraphCypherQAChain.from_llm(
    ChatOpenAI(temperature=0),
    graph=kg,
    verbose=True ,
    cypher_prompt=CYPHER_GENERATION_PROMPT,
)

def question_with_graph_cypher(question: str) -> str:
    response = cypherChain.run(question)
    print(response)


if __name__ == "__main__":
    questions = ["Which topics has Oriol Vinals written about?",
                 "Summarize Oriol Vinyals research."]
    for question in questions:
        print(f"\n> {question}")
        question_with_graph_cypher(question)
