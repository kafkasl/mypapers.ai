from knowledge_base.download import download_papers_by_id, get_arxiv_id
from knowledge_graph.ingest import add_papers_to_graph
from knowledge_graph.create_reference_edges import create_reference_edges
from knowledge_base.find import get_category_papers
from knowledge_graph.db import paper_exists
from utils.logger import logger

import sys
from datetime import date, timedelta

logger.info("Script started.")

def add_papers(target_date=None):
    logger.info("Function add_papers started.")
    category = 'cs.CL'
    logger.info(f"Category set to: {category}")

    added = 0
    logger.info("Fetching papers...")
    results = get_category_papers(category=category, max_results=1000)
    for paper in results:
        logger.info(f"Processing paper: {paper.entry_id}")
        paper_id = get_arxiv_id(paper.entry_id)
        if paper_exists(paper_id):
            logger.info(f"Paper already exists: {paper_id}")
            continue

        pub_date = paper.published.date()
        logger.info(f"Published date: {pub_date}")

        # If the publication date is earlier than the target date, stop the program
        if target_date is not None and pub_date < target_date:
            logger.info(f"Publication date {pub_date} is earlier than target date {target_date}. Exiting.")
            sys.exit(0)

        retries = 3
        done = False
        while retries > 0 and not done:
            try:
                logger.info(f"Adding {paper_id}")
                added_papers = download_papers_by_id(paper_ids=[paper_id], download_references=True, max_depth=1)
                # add_papers_to_graph(files)
                added += added_papers
                done = True
            except Exception as e:
                logger.info(f"Error processing paper {paper_id}: {e}")
                retries -= 1
        if not done:
            logger.info("Failed to process paper after retries, exiting.")
            sys.exit(1)

    logger.info(f"Added {added} papers to the graph for target date {target_date}")

if __name__ == "__main__":
    logger.info("Running add_papers from main.")
    # yesterday = date.today() - timedelta(days=3)
    yesterday = date.today() - timedelta(days=2)
    logger.info(f"Yesterday's date: {yesterday}")
    # add_papers(target_date=yesterday)
    add_papers()
