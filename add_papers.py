from knowledge_base.download import download_papers_by_id, get_arxiv_id
from knowledge_graph.ingest import add_papers_to_graph
from knowledge_graph.create_reference_edges import create_reference_edges
from knowledge_base.find import get_category_papers
from knowledge_graph.db import paper_exists

import sys
from datetime import date, timedelta

print("Script started.")

def add_papers(target_date=None):
    print("Function add_papers started.")
    category = 'cs.CL'
    print(f"Category set to: {category}")

    added = 0
    print("Fetching papers...")
    for paper in get_category_papers(category=category, max_results=1000):
        print(f"Processing paper: {paper.entry_id}")
        paper_id = get_arxiv_id(paper.entry_id)
        if paper_exists(paper_id):
            print(f"Paper already exists: {paper_id}")
            continue

        pub_date = paper.published.date()
        print(f"Published date: {pub_date}")

        # If the publication date is earlier than the target date, stop the program
        if target_date is not None and pub_date < target_date:
            print(f"Publication date {pub_date} is earlier than target date {target_date}. Exiting.")
            sys.exit(0)

        retries = 3
        done = False
        while retries > 0 and not done:
            try:
                print(f"Adding {paper_id}")
                files = download_papers_by_id(paper_ids=[paper_id], download_references=True, max_depth=1)
                add_papers_to_graph(files)
                added += 1
                done = True
            except Exception as e:
                print(f"Error processing paper {paper_id}: {e}")
                retries -= 1
        if not done:
            print("Failed to process paper after retries, exiting.")
            sys.exit(1)

    print(f"Added {added} papers to the graph until {pub_date}")

if __name__ == "__main__":
    print("Running add_papers from main.")
    yesterday = date.today() - timedelta(days=2)
    print(f"Yesterday's date: {yesterday}")
    add_papers(target_date=yesterday)
