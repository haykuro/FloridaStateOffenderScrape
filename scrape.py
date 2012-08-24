# imports
import urllib2
from urlparse import urlparse
from bs4 import BeautifulSoup

# URLs
inmatePopulationSearchURL = 'http://www.dc.state.fl.us/ActiveInmates/list.asp?DataAction=Filter&SexOffOnly=0&dcnumber=&LastName=&FirstName=&SearchAliases=on&Sex=M&Race=ALL&OffenseCategory=ALL&ClassificationStatus=ALL&CurrentCustody=ALL&IdentifierType=ALL&Identifier=&EyeColor=ALL&HairColor=ALL&FromAge=&ToAge=&FromWeight=&ToWeight=&FromHeightFeet=&FromHeightInches=&ToHeight=&ToHeightFeet=&ToHeightInches=&ZipCode=&ScarType=ALL&ScarLocation=ALL&ScarDescription=&photosonly=on&nophotos=on&items=50&CommitmentCounty=ALL&subjecttype=ALL&facility=ALL&workskill=ALL'


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

    def ScrapeTable(self, htmlContent):
        soup = BeautifulSoup(htmlContent, 'lxml')
        contentContainer = soup.find(id="dcCSScontentContainer")
        table = contentContainer.find_all('table')[2]
        ths = table.find_all('th')
        headers = []
        for item in ths:
            headers.append(item.get_text())

        links = table.find_all('a')
        for link in links:
            print link.get('href')
        return headers


# Main App Function
class Main():
    def __init__(self):
        DataScraper = OffenderScraper()

        # Pull Data
        try:
            cache = open('/tmp/populationSearch', 'r+b')
            cacheContents = cache.read()
            cache.close()

            if(cacheContents.__len__ > 0):
                    content = cacheContents
            else:
                    content = DataScraper.GetURL(inmatePopulationSearchURL)
        except IOError:
            cache = open('/tmp/populationSearch', 'w+b')
            content = DataScraper.GetURL(inmatePopulationSearchURL)
            cache.write(content)
            cache.close()

        print DataScraper.ScrapeTable(content)
        return None


# execute
Main()
