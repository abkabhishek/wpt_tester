


class NAVman:

    def __init__(self,name,wlcm,itemList,endMSG):
        self.name=name
        self.welcomeMSG=wlcm
        self.itemList=itemList
        self.endMSG=endMSG

        pass

    def welcome(self,):
        print('*' * 100)
        print('{s:{c}^{n}}'.format(s=self.welcomeMSG, n=100, c='#'))


    def pageShow(self):
        print('List of options')
        for item in self.itemList:
            print ('{}. {}'.format(item[0],item[1]))

    def getInput(self,inputMsg):
        x=input(inputMsg)
        # x=x.strip()
        y=int(x)
        return  y

    def end(self,):
        print('Exiting...'+self.name)
        print(self.endMSG)
        print('*' * 100)