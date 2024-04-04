import os
from knowledge_base.arxiv import Arxiv
from find import find_paper_by_title
from utils.logger import logger
from collections import deque

def download_paper(paper_id: str, save_path: str = "./papers"):
    """
    Download the paper's PDF given its ArXiv ID.
    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    try:
        logger.info(f"Loading '{paper_id}'")
        paper = Arxiv(paper_id)
        paper.load(save=False)
        logger.info(f"Getting references for paper '{paper.title}'")
        refs = paper.get_refs()
        logger.info(f"Found {len(refs)} references")
        paper.save()
    except Exception as e:
        logger.error(f"Failed to download paper '{paper_id}': {e}")

    return paper


def download_papers_by_id(paper_ids=("1712.01815"), download_references=True, max_papers=100)
    paper_queue = deque(paper_ids)  # Initialize the queue with the initial paper IDs
    seen = set()  # Use a set for faster lookup
    downloaded_papers = 0

    while paper_queue and downloaded_papers < max_papers:
        current_paper_id = paper_queue.popleft()  # Get the next paper ID from the queue
        if current_paper_id in seen:
            continue

        seen.add(current_paper_id)
        paper = download_paper(current_paper_id)
        downloaded_papers += 1

        # Add new references to the queue without exceeding the max_papers limit
        if download_references and downloaded_papers < max_papers:
            paper_queue.extend(map(lambda ref: ref['id'], paper.references))


if __name__ == "__main__":
    # title = "AlphaStar Unplugged: Large-Scale Offline Reinforcement Learning"
    # paper_id = find_paper_by_title(title)

    paper_ids = [
        "2308.03526", # AlphaStar Unplugged: Large-Scale Offline Reinforcement Learning
        "1712.01815", # Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm
        # "2403.00504", # Learning and Leveraging World Models in Visual Representation Learning
        # "2402.07630", # G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering
        # "2403.05530", # Gemini 1.5: Unlocking multimodal understanding across millions of tokens of context
        # "2307.09288", # Llama 2: Open Foundation and Fine-Tuned Chat Models
    ]

    download_papers_by_id(paper_ids=paper_ids, download_references=True, max_papers=100)

