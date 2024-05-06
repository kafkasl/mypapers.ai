from knowledge_base.arxiv_paper import get_paper_id
from datetime import datetime, timezone
import arxiv

DEFAULT_MAX_RESULTS = 5
client = arxiv.Client()


def find_paper_by_title(title: str) -> str:
    """
    Find a paper by its title and return its ArXiv ID.
    """
    paper_id = get_paper_id(title)
    if paper_id:
        return paper_id
    else:
        raise ValueError("Paper not found.")


# this searches by keyword
def search_by_query(query, max_results=DEFAULT_MAX_RESULTS):
    search = arxiv.Search(
        query = query,
        max_results = max_results,
        sort_by = arxiv.SortCriterion.SubmittedDate
        )

    results = client.results(search)
    return results

def search_by_title(title, max_results=DEFAULT_MAX_RESULTS):
    search = arxiv.Search(query = f"ti:{title}", max_results = max_results)
    return client.results(search)

def search_by_author(author, max_results=DEFAULT_MAX_RESULTS):
    search = arxiv.Search(query = f"au:{author}", max_results = max_results)
    return client.results(search)

def search_by_id(paper_id, max_results=DEFAULT_MAX_RESULTS):
    search = arxiv.Search(id_list=[paper_id], max_results=max_results)
    return client.results(search)

def get_category_papers(category='cs.CL', max_results=DEFAULT_MAX_RESULTS):
    today = datetime.now(timezone.utc).strftime('%Y%m%d')
    # date filtering is not listed in the API but it's available. More info: https://groups.google.com/g/arxiv-api/c/mAFYT2VRpK0
    # https://export.arxiv.org/api/query?search_query=submittedDate:[200901130630+TO+200901131645]&max_results=200
    # date_range = f"[{today}0000+TO+{today}2359]"
    # encoded_date_range = urllib.parse.quote_plus(date_range)

    search = arxiv.Search(
        query=f"cat:{category}",
        # query=f"cat:{category} AND submittedDate:{date_range}",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    results = client.results(search)

    return results

if __name__ == "__main__":

    results = get_category_papers()
    for r in results:
        print(r.title[:50], r.published.strftime('%Y-%m-%d %H:%M:%S %Z'))
    
    # title = "AlphaStar Unplugged: Large-Scale Offline Reinforcement Learning"

    # print(f"\n\nBy keyword search: {title}\n")
    # results = search_by_query(title)
    # for r in results:
    #     print(f"[{r.entry_id.split('/')[-1]}] {r.title}")

    # print(f"\n\nBy simple title: {title}\n")
    # results = search_by_title(title)
    # for r in results:
    #     print(f"[{r.entry_id.split('/')[-1]}] {r.title}")

    # author = "Oriol Vinyals"
    # print(f"\n\nBy author search: {author}\n")
    # results = search_by_author(author)
    # for r in results:
    #     print(f"[{r.entry_id.split('/')[-1]}] {r.title}")


    # paper_id = find_paper_by_title(title)
    # print(f"Paper ID: {paper_id}")
    # print("\n\nBy ID search: \n")
    # results = search_by_id(paper_id)
    # for r in results:
    #     print(f"[{r.entry_id.split('/')[-1]}] {r.title}")
