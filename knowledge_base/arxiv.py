import os
import re
import arxiv
import PyPDF2
import json
import requests
from requests.adapters import HTTPAdapter, Retry

from glob import glob
from utils.logger import logger
from typing import Optional

paper_id_re = re.compile(r'https://arxiv.org/abs/(\d+\.\d+)')

def retry_request_session(retries: Optional[int] = 5):
    # we setup retry strategy to retry on common errors
    retries = Retry(
        total=retries,
        backoff_factor=0.1,
        status_forcelist=[
            408,  # request timeout
            500,  # internal server error
            502,  # bad gateway
            503,  # service unavailable
            504   # gateway timeout
        ]
    )
    # we setup a session with the retry strategy
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def get_paper_id(query: str, handle_not_found: bool = True):
    """Get the paper ID from a query.

    :param query: The query to search with
    :type query: str
    :param handle_not_found: Whether to return None if no paper is found,
                             defaults to True
    :type handle_not_found: bool, optional
    :return: The paper ID
    :rtype: str
    """
    special_chars = {
        ":": "%3A",
        "|": "%7C",
        ",": "%2C",
        " ": "+"
    }
    # create a translation table from the special_chars dictionary
    translation_table = query.maketrans(special_chars)
    # use the translate method to replace the special characters
    search_term = query.translate(translation_table)
    # init requests search session
    session = retry_request_session()
    # get the search results
    res = session.get(f"https://www.google.com/search?q={search_term}&sclient=gws-wiz-serp")
    try:
        # extract the paper id
        paper_id = paper_id_re.findall(res.text)[0]
    except IndexError:
        if handle_not_found:
            # if no paper is found, return None
            return None
        else:
            # if no paper is found, raise an error
            raise Exception(f'No paper found for query: {query}')
    return paper_id

def find_by_id(paper_id: str, directory: str = 'papers') -> Optional[str]:
    """
    Find the filename without extension matching a given paper ID within a specified directory.

    :param paper_id: The ID of the paper.
    :param directory: The directory to search in, defaults to 'papers'.
    :return: The matching filename without extension if found, None otherwise.
    """
    file_pattern = f'{directory}/*-{paper_id}.*'
    matching_files = glob(file_pattern)
    if matching_files:
        # Assuming there's only one match per ID, and removing the extension and path
        return os.path.splitext(matching_files[0])[0]

def generate_path(title: str, paper_id: str, directory: str = 'papers') -> str:
    """
    Generate a "clean" filename given a paper title and ID.

    :param title: The title of the paper.
    :param paper_id: The ID of the paper.
    :param extension: The file extension, defaults to 'json'.
    :return: A clean filename string.
    """
    # Remove unsafe characters and truncate to ensure the filename is valid
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)[:150]  # Truncate and remove unsafe characters
    filename = f'{directory}/{safe_title}-{paper_id}'
    return filename

class Arxiv(object):
    refs_re = re.compile(r'\n(References|REFERENCES)\n')
    references = []
    get_id = re.compile(r'(?<=arxiv:)\d{4}.\d{5}')

    def __init__(self, paper_id: str):
        """Object to handle the extraction of an ArXiv paper and its
        relevant information.

        :param paper_id: The ID of the paper to extract
        :type paper_id: str
        """
        self.id = paper_id
        self.url = f"https://export.arxiv.org/pdf/{paper_id}.pdf"
        # initialize the requests session
        self.session = requests.Session()

    def load(self, save: bool = False):
        """Load the paper from the ArXiv API or from a local file
        if it already exists. Stores the paper's text content and
        meta data in self.content and other attributes.

        :param save: Whether to save the paper to a local file,
                     defaults to False
        :type save: bool, optional
        """
        file_path = find_by_id(self.id)
        if file_path:
            logger.info(f'Loading {file_path} from file')
            with open(f"{file_path}.json", 'r') as fp:
                attributes = json.loads(fp.read())
            for key, value in attributes.items():
                setattr(self, key, value)
        else:
            res = self.session.get(self.url)
            # get meta for PDF
            self._download_meta()
            file_path = generate_path(self.title, self.id)
            with open(f'{file_path}.pdf', 'wb') as fp:
                fp.write(res.content)
            # extract text content
            self._convert_pdf_to_text()
            if save:
                self.save()

    def get_refs(self):
        """Get the references for the paper.
        Note: it only returns Arxiv references matched with the regex .get_id

        :return: The references for the paper
        :rtype: list
        """
        logger.info(f'Extracting references for {self.id}')
        if len(self.references) == 0:
            content = self.content.lower()
            matches = self.get_id.findall(content)
            matches = list(set(matches))
            self.references = [{"id": m} for m in matches]
        logger.info(f'Found {len(self.references)} references')
        return self.references

    def _convert_pdf_to_text(self):
        """Convert the PDF to text and store it in the self.content
        attribute.
        """
        text = []
        logger.info(f'Converting {self.id} to text')
        file_path = find_by_id(self.id)
        with open(f'{file_path}.pdf', 'rb') as f:
            # create a PDF object
            pdf = PyPDF2.PdfReader(f)
            # iterate over every page in the PDF
            for page in range(len(pdf.pages)):
                # get the page object
                page_obj = pdf.pages[page]
                # extract text from the page
                text.append(page_obj.extract_text())
        text = "\n".join(text)
        self.content = text

    def _download_meta(self):
        """Download the meta information for the paper from the
        ArXiv API and store it in the self attributes.
        """
        search = arxiv.Search(
            query=f'id:{self.id}',
            max_results=1,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        result = list(search.results())
        if len(result) == 0:
            raise ValueError(f"No paper found for paper '{self.id}'")
        result = result[0]
        # remove 'v1', 'v2', etc. from the end of the pdf_url
        result.pdf_url = re.sub(r'v\d+$', '', result.pdf_url)
        self.authors = [author.name for author in result.authors]
        self.categories = result.categories
        self.comment = result.comment
        self.journal_ref = result.journal_ref
        self.source = result.pdf_url
        self.primary_category = result.primary_category
        self.published = result.published.strftime('%Y%m%d')
        self.summary = result.summary
        self.title = result.title
        self.updated = result.updated.strftime('%Y%m%d')
        logger.info(f"Downloaded metadata for paper '{self.id}'")

    def save(self):
        """Save the paper to a local JSON file.
        """
        file_path = generate_path(self.title, self.id)
        with open(f'{file_path}.json', 'w') as fp:
            json.dump(self.__dict__(), fp, indent=4)

    def get_meta(self):
        """Returns the meta information for the paper.

        :return: The meta information for the paper
        :rtype: dict
        """
        fields = self.__dict__()
        # drop content field because it's big
        fields.pop('content')
        return fields

    def _clean_text(self, text):
        text = re.sub(r'-\n', '', text)
        return text

    def __dict__(self):
        return {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'source': self.source,
            'authors': self.authors,
            'categories': self.categories,
            'comment': self.comment,
            'journal_ref': self.journal_ref,
            'primary_category': self.primary_category,
            'published': self.published,
            'updated': self.updated,
            'content': self.content,
            'references': self.references
        }

    def __repr__(self):
        return f"Arxiv(paper_id='{self.id}')"