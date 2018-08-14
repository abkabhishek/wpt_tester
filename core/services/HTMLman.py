import requests
import re
from bs4 import BeautifulSoup as BS4

class HTMLman:

    def __init__(self):
        pass

    def getHTML(self,url):
        self.html = requests.get(url)
        return self.html

    def findTextInHTML(self,datahtml,url,searchPhrase):

        pattern = re.compile("^https?:\/\/")
        soup = BS4(datahtml.content, 'html.parser')
        anchors = soup.find_all('a')
        for a in anchors:
            href = a.get('href')
            #   href=str(href)
            href=str(href).encode('utf-8','ignore').strip()
            if(pattern.match(href)):
                print ("%s,%s" %(url,href))
            # print ("%s,%s" %(url,href))

    def getHREFfromATag(self,datahtml,OutputfileName,searchPhrase=''):
        pattern = re.compile(searchPhrase)
        soup = BS4(datahtml.content, 'html.parser')
        anchors = soup.find_all('a')
        with open(OutputfileName,'a+') as fl:
            for a in anchors:
                href = a.get('href')
                href=str(href)
                # href=str(href).encode('utf-8','ignore').strip()
                if (searchPhrase!=''):
                    if (pattern.match(href)):
                        print ("%s" %(href))
                        fl.write("%s\n" %(href))
                # print ("%s,%s" %(url,href))

if __name__ == "__main__":
    url='https://guest1:guest@supportn2.startpage.com/nl/'
    # searchString='string to find inside urls'
    output='URLsList_Support_Homepage_15Mar18_v3.csv'
    searchPhrase="^http"
    htm=HTMLman()
    data=htm.getHTML(url)
    htm.getHREFfromATag(data,output,searchPhrase)
    # htm.findTextInHTML(url1,searchString)

    # filename = 'C:/Users/Arijit/Desktop/TEMPORARY_DELETE/eu9_family_list.csv'
    # with open(filename) as file:
    #     for line in file:
    #         # l = line.strip()
    #         l = str(line).encode('utf-8').strip()
    #         datahtml=htm.getHTML(l)
    #         htm.findTextInHTML(datahtml,l,searchString)