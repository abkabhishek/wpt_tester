import base64

'''This method takes a file as input and returns base64 encoded string in return'''

def encode(self,file):

    data = open(file,'rb') # reading file in binary mode
    binary = data.read()
    return base64.encodestring(binary)
