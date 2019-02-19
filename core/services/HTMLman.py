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
    url='https://www.google.com/'
    # searchString='string to find inside urls'
    output='test_sample.csv'
    searchPhrase="^http"
    htm=HTMLman()
    data=htm.getHTML(url)
    htm.getHREFfromATag(data,output,searchPhrase)
