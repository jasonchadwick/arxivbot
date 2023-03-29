
import urllib
import requests
from bs4 import BeautifulSoup

from result_info import ResultInfo


class Scraper:
    QUERY_PREFIX = 'https://arxiv.org/search/advanced?'
    DEFAULT_SEARCH_QUERY = {
        'advanced':'',
        'terms-0-operator':'AND',
        'terms-0-term':'quantum computing',
        'terms-0-field':'all',
        'terms-1-operator':'OR',
        'terms-1-term':'"quantum circuit"',
        'terms-1-field':'all',
        'terms-2-operator':'OR',
        'terms-2-term':'"qubit"',
        'terms-2-field':'all',
        'terms-3-operator':'OR',
        'terms-3-term':'"qutrit"',
        'terms-3-field':'all',
        'terms-4-operator':'OR',
        'terms-4-term':'"qudit"',
        'terms-4-field':'all',
        'classification-physics_archives':'all',
        'date-filter_by':'all_dates',
        'date-year':'',
        'date-from_date':'',
        'date-to_date':'',
        'date-date_type':'submitted_date',
        'abstracts':'show',
        'size':'50',
        'order':'-announced_date_first',
    }

    def __init__(self, url):
        self.url = url
        self._result_nodes = None
        self._results = None

    def scrape(self):
        self._setup_result_nodes()
        self._setup_results()

    @classmethod
    def get_arxiv_search_query(cls, params=(), prefix=None, **kw_params):
        query_params = dict(cls.DEFAULT_SEARCH_QUERY)
        query_params.update(params)
        query_params.update(kw_params)
        if prefix is None:
            prefix = cls.QUERY_PREFIX
        return prefix + urllib.parse.urlencode(query_params)

    @classmethod
    def with_search_query(cls, params=(), **kw_params):
        url = cls.get_arxiv_search_query(params=params, **kw_params)
        return cls(url)

    @property
    def results(self):
        if self._results is None:
            self._setup_results()
        return self._results

    def _setup_results(self):
        self._results = tuple(ResultInfo.from_node(node) for node in self.result_nodes)

    @property
    def result_nodes(self):
        if self._result_nodes is None:
            self._setup_result_nodes()
        return self._result_nodes

    def _setup_result_nodes(self):
        self._result_nodes = self._scrape_nodes(self.url)

    @staticmethod
    def _scrape_nodes(url):
        response = requests.get(url)
        assert 200 <= response.status_code < 400, (
            'URL returned status code {}: {}'.format(response.status_code, url))

        page = BeautifulSoup(response.content, 'html.parser')
        nodes = page.body.find_all('li', attrs={'class':'arxiv-result'})
        return nodes
