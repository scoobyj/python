#!/usr/local/bin/python2.7
# encoding: utf-8
'''
com.commerce.support.highcpu.parseData -- shortdesc

@author:     Jeff Johnson


'''
from sys import version_info
from itertools import islice
import glob, os , pprint ,os.path, re


                                       
def doprocessjavacore(filename):
    with open(filename) as f:
                for line in f:
                    if line.startswith('1TIDATETIME'):
                        global jctime
                        jctime = line.split("at ",1)[1]
                        print (jctime)
                    if "native thread ID:" in line:
                                global threadId
                                threadId=line.split("ID:")[1].split(",")[0]
                    if line.startswith('3XMTHREADINFO      "'):
                           global threadName
                           threadName = line.split('"')[1].split('"')[0]
                           jcdata = [jctime,threadId,threadName]
                           print(jcdata)  

def doprocesstop(filename):
    with open(filename) as t:
            for line in t:
                if line.startswith("top"):
                    topdata = []
                    topdata.append(line)
                                      #print(topdata)
                    for i in range(4):
                        topdata.append( ''.join(islice(t,4)))
                        print(topdata)                          
                                         


def main():
    py3 = version_info[0] > 2 #creates boolean value for test that Python major version > 2

    if py3:
        response = input("Please enter directory where high cpu data resides: ")
    else:
        response = raw_input("Please enter directory where high cpu data resides: ")    
  
    for filename in glob.glob(os.path.join(response,'java*')):
          doprocessjavacore(filename)
                              
                              
                              
    for filenamet in glob.glob(os.path.join(response,'top*')):
            doprocesstop(filename)
                        
                                         
if __name__ == "__main__":
    main()
             