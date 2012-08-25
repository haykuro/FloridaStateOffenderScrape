### IMPORTS ###
# regular expressions
import re
# md5 sums
import md5
# Network IO
import urllib2
# URL Parser
from urlparse import urlparse
# BeautifulSoup for Scraping
from bs4 import BeautifulSoup
### END IMPORTS ###

### VARIABLES ###
# URLs
inmatePopulationSearchURL = 'http://www.dc.state.fl.us/ActiveInmates/list.asp?DataAction=Filter&SexOffOnly=0&dcnumber=&LastName=&FirstName=&SearchAliases=on&Sex=M&Race=ALL&OffenseCategory=ALL&ClassificationStatus=ALL&CurrentCustody=ALL&IdentifierType=ALL&Identifier=&EyeColor=ALL&HairColor=ALL&FromAge=&ToAge=&FromWeight=&ToWeight=&FromHeightFeet=&FromHeightInches=&ToHeight=&ToHeightFeet=&ToHeightInches=&ZipCode=&ScarType=ALL&ScarLocation=ALL&ScarDescription=&photosonly=on&nophotos=on&items=50&CommitmentCounty=ALL&subjecttype=ALL&facility=ALL&workskill=ALL'
### END VARIABLES ###


# classes, functions
class OffenderScraper:
    def GetURL(self, url):
        # Parse URL for '//' (e.g.: 'http://')
        urlschema = urlparse(url)

        if urlschema.netloc == '':
            url = 'http://' + urlschema.path
        else:
            url = urlschema.geturl()

        content = ""
        # Caching based on md5's of URL's
        cacheFileName = md5.new(url).hexdigest()
        try:
            # try to open cache
            cache = open('/tmp/' + cacheFileName, 'r+b')
            cacheContents = cache.read()
            cache.close()

            if(cacheContents.__len__ > 0):
                # cache is not blank
                content = cacheContents
            else:
                # cache is blank, fill it.
                response = urllib2.urlopen(url)
                content = response.read()
                cache.write(content)
        except IOError:
            # cache does not exist, create it.
            cache = open('/tmp/' + cacheFileName, 'w+b')
            response = urllib2.urlopen(url)
            content = response.read()
            cache.write(content)
            cache.close()

        return content

    def ScrapeTableLinks(self, htmlContent):
        soup = BeautifulSoup(htmlContent, 'lxml')
        contentContainer = soup.find(id="dcCSScontentContainer")
        table = contentContainer.find_all('table')[2]
        ths = table.find_all('th')
        headers = []
        for item in ths:
            headers.append(item.get_text())

        HTMLlinks = table.find_all('a')
        links = []
        for link in HTMLlinks:
            # Only parse links that lead to an offender detail page.
            if "detail.asp" in link.get('href'):
                links.append(link.get('href'))
        return links


# Main App Function
class Main():
    def __init__(self):
        DataScraper = OffenderScraper()

        # ScrapeTableLinks
        DetailPageLinks = DataScraper.ScrapeTableLinks(DataScraper.GetURL(inmatePopulationSearchURL))

        # Get Offender Data
        for link in DetailPageLinks:
            content = DataScraper.GetURL('http://www.dc.state.fl.us/ActiveInmates/' + link)
            print content
            break
        return None


# execute
Main()
