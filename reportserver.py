"""
Download from SQL Report Dashboard
"""
import urllib.parse
from enum import Enum

from bs4 import BeautifulSoup
from requests import Session


class ReportFormat(Enum):
    """
    File formats to download reports
    """
    CSV = 'csv'
    EXCEL = 'xls'
    XML = 'xml'

class ReportServer:
    """
    Use to download files from Report Server.

    :param report_server:
        URL to access the Report Server
    """

    def __init__(self, report_server):
        self.report_server = report_server
        self._session = None

    def login(self, username, password):
        """
        Login on Report Server.

        :param username:
            User id
        :type username:
            `string`
        :param password:
            Password.
        :type password:
            `string`
        """
        session = Session()
        itauth = session.get(self.report_server)
        (fields, action) = self._parse_login_form(itauth)
        fields['txtUserName'] = username
        fields['txtPassword'] = password
        resp = session.post(f"{self.report_server}{action}", fields)
        if resp.status_code == 200:
            self._session = session
        else:
            raise Exception(resp.status_code)

    @classmethod
    def _parse_login_form(cls, response):
        """
        Returns the fields and values of the form

        :param response:
            Raw response returned
        :type response:
            `Response`
        :return:
            A tuple (fields, action url)
        :rtype:
            `tuple(string, string)`
        """
        soup = BeautifulSoup(response.text, 'html.parser')
        fields = soup.select("#Form1")[0].select("input")
        result = {}
        for field in fields:
            if 'value' in field.attrs.keys():
                result[field['name']] = field['value']
            else:
                result[field['name']] = ''
        action = soup.select("#Form1")[0]["action"]
        return (result, action)

    def _check_session(self):
        """
        Checks an open session exists
        """
        if self._session is None:
            raise Exception('No login done.')

    def _download_url(self, url, target_filename):
        """
        Download to a file.

        :param url:
            URL to download from.
        :type:
            `string`
        :target_filename:
            Path to store the response.
        :type:
            `string`
        """
        self._check_session()
        resp = self._session.get(url)
        #Check successful status code
        resp.raise_for_status()
        #write to file
        with open(target_filename, 'wb') as handle:
            for block in resp.iter_content(1024):
                handle.write(block)

    def download_report(self, report_path, report_format, target_filename, other_args=None):
        """
        Downloads a report to a file.

        :param report_path:
            Path of the report on Report Server.
        :param report_format:
            :class:`ReportFormat` of the file.
        :param target_filename:
            Path to save the file.
        :param othr_args:
            (optional) `Dict` with query parameters.
        """
        #Create Query params
        query_args = {}
        query_args['rs:Format'] = report_format.value
        if not other_args is None:
            query_args.update(other_args)
        query_params = urllib.parse.urlencode(query_args)
        #Create thes final url
        report_url = f"{self.report_server}?/{urllib.parse.quote(report_path)}&{query_params}"
        #Dowloads the url
        print(f"Downloading from {report_url}")
        self._download_url(report_url, target_filename)
