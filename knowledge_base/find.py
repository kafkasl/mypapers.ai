from knowledge_base.arxiv_paper import get_paper_id
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

if __name__ == "__main__":
    title = "AlphaStar Unplugged: Large-Scale Offline Reinforcement Learning"

    print(f"\n\nBy keyword search: {title}\n")
    results = search_by_query(title)
    for r in results:
        print(f"[{r.entry_id.split('/')[-1]}] {r.title}")

    print(f"\n\nBy simple title: {title}\n")
    results = search_by_title(title)
    for r in results:
        print(f"[{r.entry_id.split('/')[-1]}] {r.title}")

    author = "Oriol Vinyals"
    print(f"\n\nBy author search: {author}\n")
    results = search_by_author(author)
    for r in results:
        print(f"[{r.entry_id.split('/')[-1]}] {r.title}")


    paper_id = find_paper_by_title(title)
    print(f"Paper ID: {paper_id}")
    print("\n\nBy ID search: \n")
    results = search_by_id(paper_id)
    for r in results:
        print(f"[{r.entry_id.split('/')[-1]}] {r.title}")
