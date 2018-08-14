
import sys
import argparse

from modules.WebPageTest import *
from modules.URLTest    import *
from services.Properties import *
from services.NAVman import *
import logging, coloredlogs


logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s]\t%(asctime)s\t%(message)s",
        datefmt = '%Y-%m-%d %H:%M:%S'
    )

logger = logging.getLogger(__name__)

coloredlogs.install(level='debug',
                    logger=logger,
                    fmt='[%(asctime)s]\t[%(levelname)s]\t   %(message)s',
                    field_styles={'levelname': {'color': 'white', 'bold': True}})


class App:
    def __init__(self):
        # #Logging Test
        # logging.info('Info : Start App')
        # logging.debug('debug : Start App')
        # logging.warning('warning : Start App')
        # logging.error('error : Start App')
        # logging.critical('critical : Start App')

        self.Modules=[[1,"WebPageTest > Start New Test from Config"],
                      [2,"WebPageTest > ReSubmit a New state Tests (input testset id)"],
                      [3,"WebPageTest > Process a Pending state Tests (input testset id)"],
                      [4,"WebPageTest > Show Test Set Table"],
                      [5,"WebPageTest > Reporting"],
                      [6,"WebPageTest > Update Record"],
                      [7,'URL Status/Redirection'],
                      [0,"Exit"]]
        try:
            self.P=PropT(".","Properties.ini")
            for item in self.P.Props:
                pass
        except AttributeError as err:
            print("Please use correct config path and pattern")
        # self.WPT=WPTRunner("configs", "web*test.ini", "../files/WPTReports","../DB/SBDB.db")
        self.URLT=URLTest()
        self.UserIn=0
        self.NAV=NAVman('AutoUtil',
                        ' Welcome to Automation Utility ',
                        self.Modules,
                        'Thanks for using Automation Utility!!!, We will keep improving it. Calling it a Day :)')


    def Autorun(self):
        self.NAV.welcome()
        print ('running module one')
        print ('completed module one')
        self.exit()

    def HomePage(self):
        self.NAV.welcome()
        self.NAV.pageShow()
        self.UserIn=self.NAV.getInput('Please input number to run that Module (0-{}) :'.format(self.Modules[-2][0]))

    def DoNext(self):
        if self.UserIn==self.Modules[0][0]:
            print ('Please run WebPageTest')
            self.WPT = WPTRunner("configs", "web*test.ini", "../files/WPTReports", "../DB/SBDB.db")
            self.WPT.runNewTest()
            self.HomePage()
        elif self.UserIn==self.Modules[1][0]:
            print ('Please run WebPageTest')
            testst = input("Please enter test set id to run : ")
            self.WPT = WPTRunner("configs", "web*test.ini", "files/WPTReports", "DB/SBDB.db")
            self.WPT.runOldTest(testst)
            self.HomePage()
        elif self.UserIn==self.Modules[2][0]:
            print ('Please run WebPageTest')
            testst = input("Please enter test set id to run : ")
            self.WPT = WPTRunner("configs", "web*test.ini", "files/WPTReports", "DB/SBDB.db")
            self.WPT.processOldTest(testst)
            self.HomePage()
        elif self.UserIn==self.Modules[3][0]:
            print ('Please run WebPageTest')
            self.WPT = WPTRunner("configs", "web*test.ini", "files/WPTReports", "DB/SBDB.db")
            self.WPT.testSetStats()
            self.HomePage()
        elif self.UserIn==self.Modules[4][0]:
            print ('Please run WebPageTest')
            print ('Please Enter New and Old Test Set ID to prepare compare reports')
            newTS = int(input("Please enter New Test set id : ").strip())
            oldTS = int(input("Please enter Old Test set id : ").strip())
            self.WPT = WPTRunner("configs", "web*test.ini", "files/WPTReports", "DB/SBDB.db")
            self.WPT.compareReport(newTS,oldTS)
            self.HomePage()
        elif self.UserIn == self.Modules[5][0]:
            print('Please run WebPageTest')
            testst = input("Please enter test set id to update : ")
            self.WPT = WPTRunner("configs", "web*test.ini", "files/WPTReports", "DB/SBDB.db")
            self.WPT.updateRecords(testst)
            self.HomePage()
        elif self.UserIn==self.Modules[6][0]:
            print ('Started URL testing module')
            self.URLT.startTest_all()
            self.HomePage()


    def exit(self):
        self.NAV.end()

    def __del__(self):
        logging.info(" - - - - - - - - - - - - - - - - - - - - - - - -")



parser = argparse.ArgumentParser(description='Automation Utility Application')
parser.add_argument('-m', '--mode',
                    help="Running MODE, 'a' for auto and 'm' for manual",
                    default='m')

results = parser.parse_args(sys.argv[1:])


Test=App()

if results.mode=='m':
    Test.HomePage()
    while (Test.UserIn!=0):
        Test.DoNext()
    Test.exit()
elif results.mode=='a':
    Test.Autorun()
