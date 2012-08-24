# imports
import urllib2
from urlparse import urlparse


# classes, functions
class OffenderScraper:
    def GetURL(self, url):
        # Parse URL for '//' (e.g.: 'http://')
        urlschema = urlparse(url)

        if urlschema.netloc == '':
            url = 'http://' + urlschema.path
        else:
            url = urlschema.geturl()

        response = urllib2.urlopen(url)
        return response.read()


# Main App Function
class Main():
    def __init__(self):
        # from bs4 import BeautifulSoup
        # soup = BeautifulSoup(OffenderScraper.getURL(''))
        DataScraper = OffenderScraper()
        print DataScraper.GetURL('www.google.com')
        return None


# execute
Main()
