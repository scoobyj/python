#!/usr/local/bin/python2.7
# encoding: utf-8

from sys import version_info
import glob, os , pprint ,os.path, re
py3 = version_info[0] > 2
if py3:
  response = input("Please enter directory where high cpu data resides: ")
else:
  response = raw_input("Please enter directory where high cpu data resides: ")    
  
for filename in glob.glob(os.path.join(response,'java*')):
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
                           
                              
for filenamet in glob.glob(os.path.join(response,'top*')):
                        with open(filenamet) as t:
                            tdata = {}
                            for line in t:
                                    #line = line.strip()
                                    if not line: continue
                                    if line.startswith('top'):
                                        if line not in tdata: tdata[line] = []
                                        top = line
                                        continue

                                    tdata[top].append(line)
                            
                                 
