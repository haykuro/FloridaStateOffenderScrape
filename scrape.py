"""
    Written by Steve Birstok (http://www.stevebirstok.com)
"""

### IMPORTS ###
# regular expressions
import re
# os path functions
import os
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
stateURL = 'http://www.dc.state.fl.us/ActiveInmates/'
inmatePopulationSearchURL = stateURL + 'list.asp?DataAction=Filter&SexOffOnly=0&dcnumber=&LastName=&FirstName=&SearchAliases=on&Sex=M&Race=ALL&OffenseCategory=ALL&ClassificationStatus=ALL&CurrentCustody=ALL&IdentifierType=ALL&Identifier=&EyeColor=ALL&HairColor=ALL&FromAge=&ToAge=&FromWeight=&ToWeight=&FromHeightFeet=&FromHeightInches=&ToHeight=&ToHeightFeet=&ToHeightInches=&ZipCode=&ScarType=ALL&ScarLocation=ALL&ScarDescription=&photosonly=on&nophotos=on&items=50&CommitmentCounty=ALL&subjecttype=ALL&facility=ALL&workskill=ALL'
### END VARIABLES ###


# classes, functions
class OffenderScraper:
    def GetURL(self, url):
        """Gets a URL's content and caches it using md5 of URL string"""
        # Parse URL for '//' (e.g.: 'http://')
        urlschema = urlparse(url)

        if urlschema.netloc == '':
            url = 'http://' + urlschema.path
        else:
            url = urlschema.geturl()

        content = ""
        # Caching based on md5's of URL's
        # Create Cache Folder
        cacheDir = '/tmp/OffenderScrape/'
        if not os.path.exists(cacheDir):
            # create if not exist
            os.makedirs(cacheDir)
        cacheFileName = md5.new(url).hexdigest()
        try:
            # try to open cache
            cache = open(cacheDir + cacheFileName, 'r+b')
            cacheContents = cache.read()

            if(len(cacheContents) > 0):
                # cache is not blank
                content = cacheContents
            else:
                # cache is blank, fill it.
                response = urllib2.urlopen(url)
                content = response.read()
                cache.write(content)
                cache.close()
        except IOError:
            # cache does not exist, create it.
            cache = open(cacheDir + cacheFileName, 'w+b')
            response = urllib2.urlopen(url)
            content = response.read()
            cache.write(content)
            cache.close()

        return content

    def ScrapeTableLinks(self, htmlContent):
        """Scrapes Tables for Links to Detail pages"""
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
                if not link.get('href') in links:
                    links.append(link.get('href'))
        return links

    def GetInmateDetails(self, detailContent, onlyShowRecords=False):
        """Scrapes Offender Detail Page"""
        soup = BeautifulSoup(detailContent, 'lxml')
        contentContainer = soup.find(id="dcCSScontentContainer")

        if onlyShowRecords == True:
            # Use regular expressions to see how many records this page reports there are
            matches = re.search("Record: ([\d\-,]+) of ([\d\-,]+)", str(contentContainer))
            return matches.group(2).strip().replace(',', '')

        inmate = {}

        mugshot = contentContainer.find('img', {'alt': 'Offender Picture'})

        if mugshot and len(mugshot) > 0:
            inmate['mugshot'] = stateURL + mugshot.get('src').strip('/')

        inmateInfoHeaders = contentContainer.find_all('td', {'width': '40%'})
        inmateInfoInfo = contentContainer.find_all('td', {'width': '60%'})
        i = 0
        info = 0
        while i < len(inmateInfoHeaders):
            try:
                inmate[inmateInfoHeaders[i].get_text().strip().replace(':', '').replace(' ', '_').lower()] = inmateInfoInfo[i].get_text().strip()
                info = info + 1
            except:
                pass
            i = i + 1
        # table = contentContainer.find_all('table')
        # '''
        # index - desc
        # 0 - (This information was current as of ...)
        # 1 - (This information was current as of ...)
        # 2 - Inmate Data
        # 3 - Mugshot
        # 4 - More Inmate Data
        # '''
        # print table
        # break
        if info > 0:
            return inmate
        return None

    def GenDetailLink(self, bookmark, sessionID):
        return 'detail.asp?Bookmark=' + str(bookmark) + '&From=list&SessionID=' + str(sessionID)


# Main App Function
class Main():
    def __init__(self):
        print '[.] Loading Offenderscraper Library.'
        DataScraper = OffenderScraper()

        print 'Loading Offenders'
        # ScrapeTableLinks
        DetailPageLinks = DataScraper.ScrapeTableLinks(DataScraper.GetURL(inmatePopulationSearchURL))
        content = DataScraper.GetURL(stateURL + DetailPageLinks[0])
        if len(content) < 0:
            print 'No content on first offender page.'
            exit()

        # Get Total Records from first Offendor page
        TotalRecords = DataScraper.GetInmateDetails(content, True)

        # Initiate the array to store our offendors
        inmates = []

        # Append first offender
        inmates.append(DataScraper.GetInmateDetails(content))

        # Get Detail Link Structure
        matches = re.search('SessionID=(\d+)', DetailPageLinks[0])
        session_id = matches.group(1)

        print '[!] Entering loop! Processing ' + str(TotalRecords) + ' records.'
        i = 1
        while i <= TotalRecords:
            content = DataScraper.GetURL(stateURL + DataScraper.GenDetailLink(i, session_id))
            if len(content) < 0:
                print 'No content on bookmark ' + str(i)
                exit()
            inmate = DataScraper.GetInmateDetails(content)
            inmates.append(inmate)
            i = i + 1

        print str(len(inmates)) + ' inmates loaded.'
        # for inmate in inmates:
        #     print inmate
        return None


# execute
Main()
