import os
from knowledge_base.constructors import Arxiv
from find import find_paper_by_title
import PyPDF2
from utils.logger import logger

def download_paper(paper_id: str, save_path: str = "./papers"):
    """
    Download the paper's PDF given its ArXiv ID.
    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    logger.info(f"Loading '{paper_id}'")
    paper = Arxiv(paper_id)
    paper.load(save=False)
    logger.info(f"Getting references for paper '{paper.title}'")
    # TODO: get references can be improved using pydantic and specific output formats
    # imo, it returns 21 references out of almost 40
    refs = paper.get_refs()
    logger.info(f"Found {len(refs)} references")
    paper.chunker()
    paper.save_chunks(include_metadata=True, path=save_path)

    paper.save()

    return paper


if __name__ == "__main__":
    # title = "AlphaStar Unplugged: Large-Scale Offline Reinforcement Learning"
    # title = "Learning and Leveraging World Models in Visual Representation Learning"
    # paper_id = find_paper_by_title(title)
    paper_id = "2402.07630" # G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering
    paper = download_paper(paper_id)
    for ref in paper.references:
        try:
            download_paper(ref['id'])
        except PyPDF2.errors.PdfReadError as e:
            logger.error(f'Error downloading {ref["id"]}: {e}')

