import sys
import re
import logging
sys.path.append("..")


from services.APIman import *
from services.Properties import *



class WPTApi:

    def __init__(self,APIkey):
        self.api_url="http://www.webpagetest.org/"
        # self.api_key="k="+APIkey
        self.api_key = APIkey

    def submitTest(self,**kwargs):
        """ it initiate test on webpagetest.org and return the response object and result url parsed from response header
        It will take following keyword argument
        testUrl = Its the test url
        locationString = its a location string (Location:Browser.Connectivity)
        fvonly = Its a first view only (1/0 = true/false)
        runCount = Its a run count (1-10)

        """

        #constructing url from passed kwargs

        params = dict(k=self.api_key, location=kwargs['locationString'], fvonly=kwargs['fvonly'], runs=kwargs['runCount'],f='json',url=kwargs['testUrl'])


        # url=self.api_url + "runtest.php?"+ self.api_key +"&location="+kwargs['locationString']+"&fvonly="+str(kwargs['fvonly'])+"&runs="+str(kwargs['runCount']) + "&f=json" + "&url=\""+kwargs['testUrl'] +"\""

        url = self.api_url + "runtest.php"

        logging.debug("Submitting test to WebpageTest with URL and : %s", url)

        r=APIman.send('GET',url, params=params)
        rurl=''
        rid=''
        logging.info("Status code recored is %s , %s", r.status_code, r.text)
        if r.status_code == 200:
            # geting result url from header values
            rurl,rid=self._getResultURLFromResponse(r)
            logging.info("RID : %s, RURL : %s", rid, rurl)
            return (r.json(),rurl,rid)
        elif r.status_code == 400:
            logging.error("Error occured : %s",r.json().status_text)
            return ('','','')
        else:
            return (r.json(),rurl,rid)

    def checkTestStatus(self,rid):
        ''' it checks the status of passed result id'''

        url=self.api_url + "testStatus.php?test=" +str(rid)

        logging.debug("Checking status of test with URL: %s",url)

        r = APIman.send('GET', url)
        if r.status_code==200:
            data = r.json()
            return data['statusText']
        else:
            return None

    def getTestResult(self):
        pass

    def cancelTest(self):
        pass

    def getLocationInfo(self):
        pass

    def _getResultURLFromResponse(self,res):
        logging.debug("Response JSON : %s :",res.json())
        res=res.json()
        rurl=res['data']['userUrl']
        rid=res['data']['testId']
        return rurl, rid

    def _getResultUrlFromHeader(self,headers):
        pat_url = re.compile(r'http.*>')
        pat_rid=re.compile(r'result/.*')
        m = pat_url.findall(headers['Link'])
        rurl=''
        rid=''

        if m:
            # print('Match found: ',m[0])
            rurl=m[0][:-1]
            d=pat_rid.findall(rurl)
            if d:
                rid=d[0][7:-1]
        else:
            # print('No match')
            logging.error('No Match for result url {}'.format(rurl))


        return rurl,rid



if __name__=="__main__":
    print ('Please uncomment the code as per requirement')
    # url=''
    # logging.basicConfig(
    #     level=logging.DEBUG,
    #     format="[%(levelname)s]\t%(asctime)s\t%(message)s",
    #     datefmt='%Y-%m-%d %H:%M:%S'
    # )
    # # if len(sys.argv)>1:
    # #     url=sys.argv[1]
    # #     print (url,end='')
    # # else:
    # #     print ('No url is supplied, Please run again with url')
    #
    # test=WPTApi('A.b118266106cf8ec70b6eab4b8ff3cb78')
    # rjson,rurl,rid=test.submitTest(testUrl="https://www.google.com",locationString="Dulles_Thinkpad:IE 11.Cable",fvonly='1',runCount='1')
    # print (rjson, rurl, rid)
    # # print (test.Prop.get('TESTURL','main_url'))
    # # print (test.Prop.get("TESTURL",'main_url'))
    # # r,rurl=test.submitTest(testUrl=url,locationString='Florida:Opera.Cable',fvonly=1,runCount=1)
    # # print (r.status_code)
    # # print (r.headers)
    # # print (rurl)
