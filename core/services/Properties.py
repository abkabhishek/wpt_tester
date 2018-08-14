import os
import sys

sys.path.append("..")


from configparser import ConfigParser
from .file_finder import *


class PropT:

    def __init__(self,dire,pattern):
        self.dir=dire
        self.pattern=pattern
        self.numbers=0
        self.directory,self.files_list=FileFinder.get_files(pattern,dire)
        self.numbers=len(self.files_list)
        if self.numbers==0:
            print ("No config file found as per passed pattern, Please check and try again")
        else:
            self.Props=[]
            for item in self.files_list:
                propObj=Properties(item)
                self.Props.append(propObj)
            print (len(self.files_list)," : files found, All files parsed")







class Properties:
    '''This is a class to manage any ini file which can be used for any config or value store'''
    configFileName="Properties.ini"  # main ini file name
    configFileName_Updated="PropertiesUpdated.ini" # Updated ini file name, it will be created whenever any value changes at run time in ini file

    def __init__(self,configFile):
        ''' this is init function to set all ini file variable as a instance variable of Properties class'''
        self.configFileName=configFile
        self.config = ConfigParser()
        self.copyAll(self.configFileName)
        self.wrapItAll(configFile)

    def copyAll(self,filename):
        self.config.read(filename)
        for section in self.config:
            for item in self.config[section]:
                setattr(self,section+'_'+item,self.config[section][item])
        print ('{s:{c}^{n}}'.format(s=' Parsing completed for ini file: {}'.format(self.configFileName),n=100,c='-'))

    def print1(self,section,item):
        ''' To print the section item '''
        print(self.config.get(section, item))

    def get(self,section,item):
        ''' To get the section item '''
        return (self.config.get(section, item))

    def _set(self,section,item,value):
        ''' To set the new or updated section item '''
        self.config.set(section,item,value)
        with open(Properties.configFileName_Updated, 'w') as configfile:
            self.config.write(configfile)
            self.copyAll(Properties.configFileName_Updated)


    def wrapItAll(self,filename):
        self.FullConf={}
        self.config.read(filename)
        for section in self.config:
            self.FullConf[section]={}
            for item in self.config[section]:
                self.FullConf[section][item] = self.config[section][item].strip()


if __name__ == "__main__":
    print('{s:{c}^{n}}'.format(s=' Module is in Direct access mode ', n=100, c='='))
    Prop=Properties()
    Prop.print1('INFO','username')
    print(Prop.get('DEV', 'username'))
    Prop._set("DEV",'username','abkjony')
    Prop._set("DEV", 'house', 'awesome')
    print (Prop.get('DEV','username'))
    print(Prop.get('DEV', 'house'))
