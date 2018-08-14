
import sys
import re
from datetime import datetime as dtm
from datetime import timedelta
import time
import json
import logging
from terminaltables import AsciiTable

sys.path.append("..")

from services.APIman import *
from services.Properties import *
from services.DBman import *
from services.FILEman import *
from bs4 import BeautifulSoup as BS4
from modules.WPT_API import *





class WPTRunner:

    def __init__(self,configDire, configPatt,outputFolder='files/WPTReports',DBFile=None,Settings='configs/webpagetest_settings.ini'):
        self.configDire=configDire
        self.configPatt=configPatt
        self.outputFolder=outputFolder
        self.DBFile=DBFile
        logging.debug("Initiating WPTRunner with passed Parameter, Config Dir : %s, config Pattern : %s, Output Folder : %s, DB : %s",configDire,configPatt,outputFolder,DBFile)

        MProp=Properties(Settings)
        self.Settings = dict(MProp.FullConf)    # getting complete config detail as dictionary



    def runNewTest(self):
        logging.info("Initiating New Test Set Run")
        try:
            self.Test = PropT(self.configDire, self.configPatt)
            if (len(self.Test.Props)>0):
                logging.info('Initiated WPT Runner for configs : %s',len(self.Test.Props))
        except AttributeError as err:
            logging.error("Please use correct config path and pattern : %s", err)
            sys.exit()

        logging.info ("Running WebPageTest for New Test Set as per parsed config files")
        for item in self.Test.Props:
            logging.info(" --- Running WebPageTest for a config --- ")
            FullConf=dict(item.FullConf)
            test=WebPageTest(self.outputFolder,self.DBFile,self.Settings,FullConf)
            test.start()

    def runOldTest(self,TestSt):
        logging.info("Initiating Old Test Run")
        test = WebPageTest(self.outputFolder, self.DBFile, self.Settings)
        test.runT(TestSt)

    def processOldTest(self,TestSt):
        logging.info("Initiating Old Test Processing")
        test = WebPageTest(self.outputFolder, self.DBFile, self.Settings)
        test.process(TestSt)

    def updateRecords(self,TestSt):
        logging.info("Initiating update Processing")
        test = WebPageTest(self.outputFolder, self.DBFile, self.Settings)
        test.updateData(TestSt)

    def compareReport(self,CurTS,OldTS):
        logging.info("Initiating Compare Reporting")
        test = WebPageTest(self.outputFolder, self.DBFile, self.Settings)
        test.reporting(CurTS,OldTS)

    def testSetStats(self):
        logging.info('initiating Test Set Stats')
        test = WebPageTest(self.outputFolder, self.DBFile, self.Settings)
        test.testSetInfo()







class WebPageTest:

    INTERNALWAIT=60
    def __init__(self,outputFolder, DBFile,Settings,Prop=None):
        ''' contructor with following paramters
        required : configFile = configFile path as per current execution directory
        required : outputFolder = outputFolder path as per current execution directory
        optional : DBFile = path of DB file in case of change
        '''

        self.confNames = {
            "modeofinput": ['TESTURL', 'modeofinput'],
            "filepath": ['TESTURL', 'filepath'],
            "main_url": ['TESTURL', 'main_url'],
            "sub_url": ['TESTURL', 'sub_url'],
            "tablename": ['PROJECT', 'tablename'],
            "SPEEDTEST": ['INFO', 'SPEEDTEST'],
            "SSL": ['INFO', 'SSL'],
            "WAIT": ['INFO', 'wait'],
            "DEBUG": ['INFO', 'DEBUG'],
            "locationString": ['WEBPAGETEST', 'location_browser_connectivity'],
            "run": ['WEBPAGETEST', 'run'],
            "fvonly": ['WEBPAGETEST', 'fvonly']
        }

        self.outputFolder = outputFolder

        if DBFile!=None:
            self.DB=DBman(DBFile)
        else:
            self.DB=DBman()
        self.Settings=Settings

        if Prop!=None:
            self.Prop=Prop
            self.tableName = str(self.Prop['PROJECT']['tablename'].strip())
            self.APIkey = str(self.Prop['WEBPAGETEST']['api_key'].strip())
            self.MonitorWait = int(self.Prop[self.confNames['WAIT'][0]][self.confNames['WAIT'][1]].strip())
        else:
            self.MonitorWait = int(self.Settings['INFO']['wait'].strip())
            self.APIkey = str(self.Settings['SETTINGS']['api_key'].strip())

        self.tableName = str(self.Settings['PROJECT']['tablename'].strip())
        self.Flman = FILEman()

        self.WPT = WPTApi(self.APIkey)

        self.SelectedTestSet=0
        self.tableString='''CREATE TABLE IF NOT EXISTS {}
                 (ID            INTEGER     PRIMARY KEY  AUTOINCREMENT,
                 TIMESTAMP      DATETIME    NOT NULL,
                 URL            TEXT        NOT NULL,
                 LOCATION       CHAR(20),
                 BROWSER        CHAR(20),
                 LOCATIONSTRING CHAR(20),
                 FVONLY         INTEGER,
                 RUN            INTEGER,
                 DATEOFTEST     DATE,
                 STATUS         CHAR(20)    NOT NULL,
                 RESULTURL      TEXT,
                 RESULTID       TEXT,
                 GRADE1         CHAR(5),
                 GRADE2         CHAR(5),
                 GRADE3         CHAR(5),
                 GRADE4         CHAR(5),
                 GRADE5         CHAR(5),
                 GRADE6         CHAR(5),
                 HTMLFILE       CHAR(100),
                 TESTSETID      INTEGER,
                 RESULTJSON     BLOB,
                 SCORE          INTEGER,
                 PARAMETER1     CHAR(100),
                 PARAMETER2     CHAR(100),
                 PARAMETER3     CHAR(100),
                 PARAMETER4     CHAR(100),
                 PARAMETER5     CHAR(100),
                 PARAMETER6     CHAR(100),
                 PARAMETER7     CHAR(100),
                 PARAMETER8     CHAR(100),
                 PARAMETER9     CHAR(100),
                 PARAMETER10    CHAR(100),
                 NOTES          TEXT);'''.format(self.tableName)

        self.LocationTable = {
            "SanFrancisco:Chrome.Cable":["SanFrancisco","Chrome"],
            "SanFrancisco:Firefox.Cable":["SanFrancisco","Firefox"],
            "SanFrancisco:Opera.Cable":["SanFrancisco","Opera"],
            "gce-us-west1-linux:Chrome.Cable":["Oregon","Chrome"],
            "gce-us-west1-linux:Opera.Cable":["Oregon","Opera"],
            "gce-us-west1-linux:Firefox.Cable":["Oregon","Firefox"],
            "Dulles_Thinkpad:IE 11.Cable":["Dulles","IE 11"],
            "Dulles_Thinkpad:Chrome.Cable":["Dulles","Chrome"],
            "Dulles_Thinkpad:Firefox.Cable":["Dulles","Firefox"],
            "Dulles_Thinkpad:Microsoft Edge.Cable":["Dulles","Microsoft Edge"],
            "NewJersey:Firefox.Cable":["NewJersey","Firefox"],
            "NewJersey:Chrome.Cable":["NewJersey","Chrome"],
            "NewJersey:Opera.Cable":["NewJersey","Opera"],
            "Colorado:Chrome.Cable":["Colorado","Chrome"],
            "Colorado:Firefox.Cable":["Colorado","Firefox"],
            "Texas2:Firefox.Cable":["Texas","Firefox"],
            "Texas2:Opera.Cable":["Texas","Opera"],
            "Texas2:Chrome.Cable":["Texas","Chrome"],
            "London2:Firefox.Cable":["London","Firefox"],
            "London2:Chrome.Cable":["London","Chrome"],
            "London2:Opera.Cable":["London","Opera"],
            "Manchester.Cable":["Manchester","IE 11"],
            "Paris.Cable":["Paris","IE 11"],
            "Italy:Chrome.Cable":["Italy","Chrome"],
            "Italy:Firefox.Cable":["Italy","Firefox"],
            "Italy:Opera.Cable":["Italy","Opera"],
            "gce-asia-east1-linux:Opera.Cable":["Taiwan","Opera"],
            "gce-asia-east1-linux:Chrome.Cable":["Taiwan","Chrome"]

        }





    def start(self):
        ''' Main running function'''
        logging.info('Starting Web page test run')
        # Below state to create new table, it should be utilized for new project or setup
        self.tableSetup()

        # For remove table
        # self.tableRemove(self.tableName)


        self.createTestSet()
        self.runT(self.SelectedTestSet)

    def runT(self,TestSt):
        self.SelectedTestSet=TestSt
        logging.info('Starting running of Tests of Test Set : %s', self.SelectedTestSet)
        logging.info('Found Records %s',len(self._getRows('new')))
        #Runnint Test Set
        self.runTestSet()
        #runnit status monitor
        self.statusMonitor()
        self.process(TestSt)
        # self.exit()

    def process(self,TestSt):
        self.SelectedTestSet=TestSt
        logging.info('Starting processing of completed Tests of Test Set : %s',self.SelectedTestSet)
        logging.info('Found Records %s',len(self._getRows('started')))
        self.checkTestStatus()
        self.processTestSet()
        self.exit()

    def updateData(self,TestSt):
        self.SelectedTestSet=TestSt
        logging.info('Starting process to update some values of Test Set : %s',self.SelectedTestSet)
        AllRows=self._getRows()
        if len(AllRows):
            logging.info("Count of rows to update : %s", len(AllRows))
            self._parseAndUpdateLocationBrowser(AllRows)
        else:
            logging.info('No row found to update')
        self.exit()


## Inner functions

    def statusMonitor(self):
        logging.info("Running Status Monitor")
        rid = self.LastRowID
        logging.debug("Monitoring Status of Result ID : %s",rid)
        startTime=dtm.now()
        stopTime=startTime+timedelta(seconds=int(self.MonitorWait))

        while stopTime>dtm.now():

            if self._monitorStatus(rid):
                logging.info("Last run test is completed")
                break
            time.sleep(WebPageTest.INTERNALWAIT)
            logging.debug("Waiting for {} seconds...".format(WebPageTest.INTERNALWAIT))
            # print(".",end='')
            sys.stdout.flush()



    def _monitorStatus(self,rid):
        statusText = self.WPT.checkTestStatus(rid)
        if (statusText == 'Test Complete'):
            return True
        else:
            return False



    def _parseAndUpdateLocationBrowser(self,AllRows):
        ''' This will check if Browser and Location value is blank'''
        for row in AllRows:
            if row['LOCATION'] == row['BROWSER']:
                location=self.LocationTable[row['LOCATIONSTRING']][0]
                browser=self.LocationTable[row['LOCATIONSTRING']][1]
                sql = "UPDATE {} SET LOCATION='{}', BROWSER='{}' WHERE ID={}".format(self.tableName,location,browser,row['ID'])
                self.DB.saveIt(sql)
                logging.debug('Updated is completed and updated in DB for id : %s',row['ID'])
            else:
                logging.debug("Nothing to update for row id %s",row['ID'])

    def _makeFUllUrlsInfo(self):
        ''' this is utility function to make full url from list of main and suburls in config file'''

        urls = []
        for item in list(self.Prop[self.confNames['main_url'][0]][self.confNames['main_url'][1]].split(',')):
            urls.append(item.strip())

        # print (urls)

        subUrls = []
        for item in list(self.Prop[self.confNames['sub_url'][0]][self.confNames['sub_url'][1]].split(',')):
            subUrls.append(item.strip())

        #print(subUrls)

        self.FullUrls = []
        for item in urls:
            for subitem in subUrls:
                self.FullUrls.append(item + subitem)

        for item in self.FullUrls:
            logging.debug("Completed URL for testing : %s",item)
        self.LocationString=[]
        for item in list(self.Prop[self.confNames['locationString'][0]][self.confNames['locationString'][1]].split(',')):
            self.LocationString.append(item.strip())
        self.fvonly=int(self.Prop[self.confNames['fvonly'][0]][self.confNames['fvonly'][1]].strip())
        self.runcount=int(self.Prop[self.confNames['run'][0]][self.confNames['run'][1]].strip())

    def _getRows(self,status=None):
        if status!=None:
            sql = "SELECT * FROM {} where status='{}' and TESTSETID = {} ".format(self.tableName,status,self.SelectedTestSet)
            TestSetRows=self.DB.findChemy(sql)
            AllRows=TestSetRows.fetchall()
            return AllRows
        else:
            sql = "SELECT * FROM {} where TESTSETID = {} ".format(self.tableName,self.SelectedTestSet)
            TestSetRows=self.DB.findChemy(sql)
            AllRows=TestSetRows.fetchall()
            return AllRows

    def tableSetup(self):
        ''' this function is for creating table in db as per table string for any new project'''
        self.DB.createTable(self.tableString)

    def tableRemove(self,tableName):
        ''' this function is for removing table in db as per passed Table name'''
        self.DB.remove(tableName)

    def createTestSet(self):
        '''this function is for preparing test set'''
        self._dataSetup()

    def _dataSetup(self):
        ''' this function is for validating and saving data for test set creation'''

        self._makeFUllUrlsInfo()

        # print (self.FullUrls)
        # print (self.runcount)
        # print (self.fvonly)
        # print (self.LocationString)
        sql = "SELECT TESTSETID FROM {} WHERE TESTSETID = (SELECT max(TESTSETID) FROM {});".format(self.tableName,self.tableName)
        TestSetRows = self.DB.findChemy(sql)
        AllRows = TestSetRows.fetchall()
        logging.debug('Max Count is %s',len(AllRows))
        if (len(AllRows)==0):
            self.TesSetID=1
        else:
            self.TesSetID=int(AllRows[0]['TESTSETID'])+1
            self.SelectedTestSet = self.TesSetID

        logging.info("Test Set ID: %s",self.TesSetID)
        # AllRows=TestSetRows.fetchall() #its the case with normal sql search then AllRows above should be replaced by TestSetRows

        thistime = self._timestamp()

        for item in self.FullUrls:
            for loc in self.LocationString:
                val=[item,thistime,loc,self.fvonly,self.runcount,'new',self.TesSetID]
                sql = '''INSERT INTO {}
                        (url,timestamp,locationstring,fvonly,run,status,testsetid)
                        VALUES
                        ('{}','{}','{}',{},{},'{}',{})'''.format(self.tableName,*val)
                        
                self.DB.saveIt(sql)

        logging.info("Updated new test set in DB")

## RUNNING TEST SET

    def runTestSet(self):
        AllRows=self._getRows('new')
        if len(AllRows):
            logging.info ("URL to test : %s",len(AllRows))
            self.testStarter(AllRows)
        else:
            logging.info('No URL found to test')



    def testStarter(self,Rows):
        '''this function is to trigger the webpagetest for each row url and then saving result url and id in db'''

        for row in Rows:
            #Change below code to r,rurl,rid=WPT.submitTest(*Values)
            r,rurl,rid=self.WPT.submitTest(testUrl=row['URL'],locationString=row['LOCATIONSTRING'],fvonly=row['FVONLY'],runCount=row['RUN'])
            logging.info("Rurl : %s and RID : %s",rurl,rid)

            # self.WPT.testF(row[1],row[4],row[5],row[6])
            # rid='180227_FD_7d7f9573c0639796c0f4135f43fed93b'
            # rurl='https://www.webpagetest.org/result/180227_FD_7d7f9573c0639796c0f4135f43fed93b/'
            rstring=json.dumps(r)
            logging.debug("parsed json string is : \n %s",rstring)


            sql="UPDATE {} SET RESULTURL='{}',RESULTID='{}',STATUS='{}',RESULTJSON='{}' WHERE ID={}".format(self.tableName,rurl,rid,'started',rstring,row['ID'])
            self.LastRowID = rid
            self.DB.saveIt(sql)
        logging.debug("Last Result ID : %s",self.LastRowID)
        logging.info('Test Started and updated status for each test in DB')


    def checkTestStatus(self):
        ''' This will check the status of each result url which status is started'''

        AllRows = self._getRows('started')
        # print(len(AllRows))
        if len(AllRows):
            logging.info("URL to check status : %s", len(AllRows))
            self._getTestStatus(AllRows)
        else:
            logging.info('No URL found to check status')

    def _getTestStatus(self,rows):
        for row in rows:
            rid=row['RESULTID']
            statusText=self.WPT.checkTestStatus(rid)
            if (statusText=='Test Complete'):
                sql = "UPDATE {} SET STATUS='{}' WHERE ID={}".format(self.tableName,'completed', row['ID'])
                self.DB.saveIt(sql)
                logging.debug('Test is completed and updated in DB for id : %s',row['ID'])
            else:
                logging.debug("Test is not yet completed")

## Processing TEST SET

    def processTestSet(self):
        AllRows=self._getRows('completed')
        # print (len(AllRows))
        if len(AllRows):
            logging.info("URL to process : %s", len(AllRows))
            self._testParse(AllRows)
        else:
            logging.info('No URL found to process')

    def _testParse(self,rows):

        for row in rows:
            outputfilename=self.outputFolder+'/WPTResultHTML_'+self.tableName+'__'+str(dtm.now().day)+'_'+str(dtm.now().month)+'_'+str(dtm.now().year)+'__'+str(row['ID'])+'.html'
            self.Flman.saveHTML(str(row['RESULTURL']),outputfilename)
            data = self.Flman.getHTML(outputfilename)
            grades=self._parseGrades(data)
            
            score = 0
            for g in grades:
                score = score + self._applyScore(g)
            

            sql='''UPDATE {} 
                    SET GRADE1='{}', 
                    GRADE2='{}', 
                    GRADE3='{}', 
                    GRADE4='{}', 
                    GRADE5='{}', 
                    GRADE6='{}',
                    SCORE={},
                    HTMLFILE='{}', 
                    STATUS='{}' 
                    WHERE ID={}'''.format(self.tableName,
                                grades[0],
                                grades[1],
                                grades[2],
                                grades[3],
                                grades[4],
                                grades[5],
                                score,
                                str(outputfilename),
                                'processed',
                                row['ID'])


            # GRADE=self._parseGrades(data)

            # if GRADE=='':
            #    GRADE='No GRADE found'
            #    logging.debug('No Grading found on result page for id')
            
            
            # sql="UPDATE {} SET GRADES='{}', HTMLFILE='{}', STATUS='{}' WHERE ID={}".format(self.tableName,GRADE,str(outputfilename),'processed',row['ID'])
            self.DB.saveIt(sql)


    def _saveHTMLFile(self):
        pass

    def _saveJSONData(self):
        pass

    def _parseGrades(self,data):
        soup = BS4(data, 'html.parser')
        #print (soup)
        # print (soup.find_all(class_='grades'))
        subpart=str(soup.find_all(class_='grades'))
        soup2=BS4(subpart,'html.parser')
        items=soup2.find_all('h2')
        # print (items)
        # print (len(items))
        GRADE = list()
        if not items:
            logging.debug('No Grading found on result page')
            GRADE=list('------')

        else:
            for item in items:
                # print (item.get_text())
                # GRADE=GRADE+item.get_text()
                logging.debug('Parsed one grade is : %s',item)
                if(item==''):
                    logging.debug('No Grading found on result page')
                    GRADE.append('-')

                else:
                    GRADE.append(item.get_text())
        # print (GRADE)
        return GRADE


    def _timestamp(self):
        format = '%Y-%m-%d %H:%M:%S'
        now = dtm.now()
        return now.strftime(format)

    def _applyScore(self, grade):
        return {
                'A' : 10000,
                'B' : 9000,
                'C' : 8000,
                'D' : 7000,
                'E' : 6000,
                'F' : 5000,
                'X' : 1000,
                'N/A' : 1000}.get(grade,1000)
    
        
    def _getComapreSQL(self,**kwargs):
        '''curr_date,prev_date,curr_testset,prev_testset):
        prepare the sql query for compare report from SQL db.
        If testset not provided , latest will be picked.
        Date format - YYYY-MM-DD mandatory'''

        SELECT = '''SELECT newTable.URL "URL",newTable.location "LOCATION", newTable.browser "BROWSER", oldTable.RESULTURL "Result URL", oldTable.GRADE1||oldTable.GRADE2||oldTable.GRADE3||oldTable.GRADE4||oldTable.GRADE5||oldTable.GRADE6 "OLD-GRADES", newTable.GRADE1||newTable.GRADE2||newTable.GRADE3||newTable.GRADE4||newTable.GRADE5||newTable.GRADE6 "NEW-GRADES", newTable.RESULTURL "Result URL", CASE WHEN newTable.SCORE > oldTable.SCORE THEN "POSITIVE" WHEN newTable.SCORE < oldTable.SCORE THEN "NEGATIVE" WHEN newTable.SCORE = oldTable.SCORE THEN "NEUTRAL" END "COMPARE"'''


        WHERE = ''' WHERE oldTable.URL = newTable.URL AND oldTable.LOCATIONSTRING = newTable.LOCATIONSTRING;'''

        # following will be used when test set id is not passed
        # FROM_default = '''FROM (select * from {} where date(TIMESTAMP) = date("{}") and testsetid=(select max(testsetid) from {} where date(TIMESTAMP) = date("{}"))) oldTable, (select * from {} where date(TIMESTAMP) = date("{}") and testsetid=(select max(testsetid) from {} where date(TIMESTAMP) = date("{}"))) newTable'''.format(self.tableName,kwargs['prev_date'],self.tableName,kwargs['prev_date'],self.tableName,kwargs['curr_date'],self.tableName,kwargs['curr_date'])


        FROM = ''' FROM (select * from {} where testsetid={}) oldTable, (select * from {} where testsetid={}) newTable'''.format(self.tableName,kwargs['prev_testset'],self.tableName,kwargs['curr_testset'])
        
        if (kwargs['curr_testset']>0) and (kwargs['prev_testset']>0):
            return SELECT+FROM+WHERE
        else:
            return None


## Reporting TEST SET

    def reporting(self,NewTestSt,OldTestSt):
        logging.info('Initiating compare report preparation')
        curr_testset=NewTestSt
        prev_testset=OldTestSt
        # sql =self._getComapreSQL(curr_date='2018-04-04',prev_date='2018-04-04',curr_testset=curr_testset,prev_testset=prev_testset)
        # sql = self._getComapreSQL( curr_date='2018-04-04',prev_date='2018-04-04')
        sql = self._getComapreSQL( curr_testset=curr_testset, prev_testset=prev_testset)

        if sql!=None:
            TestSetRows=self.DB.findChemy(sql)
            AllRows=TestSetRows.fetchall()
            if len(AllRows)>0:
                logging.debug ('Fetched rows : %s',str(AllRows))


                Dtable = [['URL', 'Location','Browser', 'OLD Result URL','OLD Grading', 'New Grading', 'New Result URL', 'Result']]
                Dtable.extend(AllRows)
                table = AsciiTable(Dtable)
                print('*' * 80)
                print(' -----------------   Comparison Report of Test Set {} vs {}  ---------------------'.format(curr_testset,prev_testset))
                print (table.table)

                outputfilename = self.outputFolder + '/WPT_ComparisonReport_' + self.tableName + '__' + str(dtm.now().day) + '_' + str(
                    dtm.now().month) + '_' + str(dtm.now().year) + '__tc_' + str(curr_testset) +'vs'+str(prev_testset) + '.csv'

                self.Flman.saveCSV(outputfilename,Dtable)
            else:
                logging.info('No Rows found to compare for provided Test Sets')
            # for row in AllRows:
            #     print (row)
            #     for item in row:
            #         print (item,end=', ')
            #     print('\n')
        else:
            logging.info('No record found for passed Test Set ID : %s , %s',curr_testset,prev_testset)

## Test Set stats

    def testSetInfo(self):
        logging.info('Getting Test Set information')
        '''
        SELECT  DISTINCT TESTSETID, TIMESTAMP FROM SPONE ORDER BY TESTSETID = 'TESTSETS' : count
        
        SELECT  STATUS, COUNT(*) AS 'started' FROM SPONE WHERE TESTSETID='4' GROUP BY STATUS =  give started,processed count for passed testsetid
        '''
        THdata=[['TestSet ID', 'Date', 'Total URLs','New','Pending','Processed','Others']]
        TRdata=[]
        sql = '''SELECT  DISTINCT TESTSETID, TIMESTAMP FROM {} ORDER BY TESTSETID'''.format(self.tableName)
        AllRows = self.DB.findChemy(sql).fetchall()
        if (AllRows):
            for row in AllRows:
                sql = '''SELECT  STATUS, COUNT(*) AS 'cnt' FROM {} WHERE TESTSETID ='{}' GROUP BY STATUS'''.format(self.tableName,row['TESTSETID'])
                AllRows2 = self.DB.findChemy(sql).fetchall()
                prssed=0
                strtd=0
                neww=0
                other=0
                for row2 in AllRows2:
                    if row2['STATUS']=='processed':
                        prssed=int(row2['cnt'])
                    elif row2['STATUS']=='started':
                        strtd=int(row2['cnt'])
                    elif row2['STATUS']=='new':
                        neww=int(row2['cnt'])
                    elif row2['STATUS']!='started' and row2['STATUS']!='processed' and row2['STATUS']!='new':
                        other=int(row2['cnt'])


                TRdata.append([str(row['TESTSETID']),row['TIMESTAMP'],str(strtd+prssed+neww+other),str(neww),str(strtd),str(prssed),str(other)])
        THdata.extend(TRdata)
        logging.debug('Fetched data : %s',THdata)
        table = AsciiTable(THdata)
        print ('*'*80)
        print (' -----------------   Test Set Information  ---------------------')
        print(table.table)


    def exit(self):
        logging.info('WebPageTest completed')



if __name__=="__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s]\t%(asctime)s\t%(message)s",
        datefmt = '%Y-%m-%d %H:%M:%S')

    test=WPTRunner("../configs", "web*test.ini", "../files/WPTReports",'../DB/SBDB.db','../configs/webpagetest_settings.ini')
    # test.runNewTest()
    # test.runOldTest()
    # test.compareReport()