from knowledge_base.download import download_papers_by_id, get_arxiv_id
from knowledge_graph.ingest import add_papers_to_graph
from knowledge_graph.create_reference_edges import create_reference_edges
from knowledge_base.find import get_category_papers
from knowledge_graph.db import paper_exists

from glob import glob
import sys


def add_papers():
    category = 'cs.CL'
    papers_by_date = {}

    # Fetch papers and group by date
    added = 0
    for paper in get_category_papers(category=category, max_results=1000):
        paper_id = get_arxiv_id(paper.entry_id)
        if paper_exists(paper_id):
            continue


        pub_date = paper.published.date()
        if pub_date not in papers_by_date:
            papers_by_date[pub_date] = True
            print(f"Processing papers published on {pub_date}")
    
        retries = 3
        done = False
        while retries > 0 and not done:
            try:
                # download paper and its references
                print(f"Adding {paper_id}")
                files = download_papers_by_id(paper_ids=[paper_id], download_references=True, max_depth=1)
                add_papers_to_graph(files)
                added += 1
                done = True
            except Exception as e:
                print(f"Error processing paper {e}\n{paper}")
        if not done:
            sys.exit(1)
    
    # add at the end because the references might not exist during
    # the iteration and thsu are not added
    create_reference_edges(files=glob('papers/*.json'))

    print(f"Added {added} papers to the graph until {pub_date}")

if __name__ == "__main__":
    add_papers()