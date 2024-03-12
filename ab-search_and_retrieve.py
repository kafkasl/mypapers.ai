import os
from arxiv_bot.knowledge_base.constructors import Arxiv, get_paper_id
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def find_paper_by_title(title: str) -> str:
    """
    Find a paper by its title and return its ArXiv ID.
    """
    paper_id = get_paper_id(title)
    if paper_id:
        return paper_id
    else:
        raise ValueError("Paper not found.")

def download_paper(paper_id: str, save_path: str = "./papers"):
    """
    Download the paper's PDF given its ArXiv ID.
    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)


    paper = Arxiv(paper_id)
    paper.load(save=False)
    logger.info(f"Getting references for paper '{paper.title}'")
    # get references
    refs = paper.get_refs()
    logger.info(f"Found {len(refs)} references")
    paper.chunker()
    paper.save_chunks(include_metadata=True, path=save_path)

    paper.save()
    # Download the PDF
    # paper_pdf_url = paper.url
    # response = paper.session.get(paper_pdf_url)
    # with open(f"{save_path}/{paper_id}.pdf", "wb") as f:
    #     f.write(response.content)
    # print(f"Downloaded {paper_id} to {save_path}/{paper_id}.pdf")

if __name__ == "__main__":
    title = "AlphaStar Unplugged: Large-Scale Offline Reinforcement Learning"
    try:
        paper_id = find_paper_by_title(title)
        download_paper(paper_id)
    except ValueError as e:
        print(e)