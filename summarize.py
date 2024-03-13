#!/usr/bin/env python3
import sys
from langchain_community.document_loaders import PyPDFLoader
import os
from dotenv import load_dotenv
from langchain.chains import AnalyzeDocumentChain
from langchain.llms import OpenAI
from langchain_text_splitters import CharacterTextSplitter
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain

from langchain.chat_models import ChatOpenAI

chat = ChatOpenAI(
    model_name='gpt-3.5-turbo',
    openai_api_key = os.getenv('OPENAI_API_KEY'),
    # max_tokens=self.config.llm.max_tokens
)
# Load environment variables from a .env file
load_dotenv()

# Initialize the OpenAI client with LangChain
# llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'), model_name='gpt-3.5-turbo')

# Define a simple text splitter to handle large documents
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=2500, chunk_overlap=1000
)

map_template = """The following is a set of documents
{docs}
Based on this list of docs, please identify the main themes
Helpful Answer:"""
map_prompt = PromptTemplate.from_template(map_template)
map_chain = LLMChain(llm=llm, prompt=map_prompt)

# Reduce
reduce_template = """The following is set of summaries:
{docs}
Take these and distill it into a final, consolidated summary of the main themes.
Helpful Answer:"""
reduce_prompt = PromptTemplate.from_template(reduce_template)


# Run chain
reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

# Takes a list of documents, combines them into a single string, and passes this to an LLMChain
combine_documents_chain = StuffDocumentsChain(
    llm_chain=reduce_chain, document_variable_name="docs"
)

# Combines and iteratively reduces the mapped documents
reduce_documents_chain = ReduceDocumentsChain(
    # This is final chain that is called.
    combine_documents_chain=combine_documents_chain,
    # If documents exceed context for `StuffDocumentsChain`
    collapse_documents_chain=combine_documents_chain,
    # The maximum number of tokens to group documents into.
    token_max=2000,
)

# Combining documents by mapping a chain over them, then combining results
map_reduce_chain = MapReduceDocumentsChain(
    # Map chain
    llm_chain=map_chain,
    # Reduce chain
    reduce_documents_chain=reduce_documents_chain,
    # The variable name in the llm_chain to put the documents in
    document_variable_name="docs",
    # Return the results of the map steps in the output
    return_intermediate_steps=False,
)



# # Define the chain for summarization
# summarize_document_chain = AnalyzeDocumentChain(
#     llm=llm,
#     text_splitter=text_splitter
# )

def summarize_text(file):
# def summarize_text(text):

    loader = PyPDFLoader(file)
    pages = loader.load_and_split()
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=0
    )
    split_docs = text_splitter.split_documents(pages)

    return map_reduce_chain.run(split_docs)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: summarize.py file.txt")
        sys.exit(1)

    txt_file_path = sys.argv[1]
    # with open(txt_file_path, 'r') as txt_file:
    #     input_text = txt_file.read()

    # summary = summarize_text(input_text)
    summary = summarize_text(sys.argv[1])
    summary_file_path = txt_file_path.rsplit('.', 1)[0] + '_summary.txt'

    with open(summary_file_path, 'w') as summary_file:
        summary_file.write(summary)

    print(summary)  # Also print the summary to stdout
