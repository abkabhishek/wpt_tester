import requests
from bs4 import BeautifulSoup as BS4


class FILEman:


    def __init__(self):
        # self.query_page='https://www.webpagetest.org/result/180227_FD_7d7f9573c0639796c0f4135f43fed93b/'
        pass


    def saveHTML(self,url,fileString):
        html=requests.get(url)
        with open(fileString,'w') as outfile:
            outfile.write(str(html.content))



    def getHTML(self,fileString):
        with open(fileString, 'r') as outfile:
            data=outfile.read()
            return data

    def saveCSV(self,fileString,Data):
        with open(fileString,'a+') as outfile:
            for row in Data:
                myString = ",".join(row)
                outfile.write(myString+'\n')


if __name__ == "__main__":
    Flman=FILEman()
    # Flman.saveHTML('https://www.google.com','ResultHTML.html')

