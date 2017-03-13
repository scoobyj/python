'''
Created on Mar 10, 2017
'''
from sys import version_info
from itertools import islice
import glob, os , pprint ,os.path, re
from CodeWarrior.Standard_Suite import line

# Patterns
pat_datetime = "^1TIDATETIME\\s+Date:\\s+(\\S+) at (\\S+)"
cr_datetime = re.compile(pat_datetime)
pat_native = "^3XMTHREADINFO1\\s+\(native thread ID:(\\S+)(.*)"
cr_native = re.compile(pat_native)
pat_tname = "^3XMTHREADINFO\\s+\\S(\\S+\\s\\S\\s\\S+)\\S(.*)"
cr_tname = re.compile(pat_tname)
pat_top = "^top\\s\\S\\s(\\S+)(.*)"
cr_top = re.compile(pat_top)
pat_topd = "(\\S+)\\s(.*)\\s\\S\\s(\\S+)(.*)"
cr_topd = re.compile(pat_topd)
pat_time = "(\\S+)\\s(\\S+)\\s(\\S+\\s:\\s\\S+)"
cr_time = re.compile(pat_time)
      
jcdata = []  
jctime = []
topdata = []   
      
                                       
def doprocessjavacore(filename):
    with open(filename) as f: 
                for line in f:
                    j = cr_datetime.search(line)
                    if j:
                       jctime = j.group(2)
                    n = cr_native.search(line)
                    if n:
                        global threadId
                        threadId = n.group(1)
                    t = cr_tname.search(line)
                    if t:
                        global threadName
                        threadName = t.group(1)
                        tmp = [jctime,threadId,threadName]
                        global jcdata
                        jcdata.append(tmp)
                return jcdata

def doprocesstop(filename):
    with open(filename) as t:
            for line in t:
                global topdata
                tt = cr_top.search(line)
                topdata.append(line)
                if tt:
                    toptime = tt.group(1)
                    
                    for i in range(16):
                        topdata.append(t.next())
            return topdata
                       


def main():
    py3 = version_info[0] > 2 #creates boolean value for test that Python major version > 2

    if py3:
        response = input("Please enter directory where high cpu data resides: ")
    else:
        response = raw_input("Please enter directory where high cpu data resides: ")    
  
    for filename in glob.glob(os.path.join(response,'java*')):
          doprocessjavacore(filename)
    print jcdata
    
        
    for filename in glob.glob(os.path.join(response,'top*')):
            doprocesstop(filename)
            print topdata    
            
                                
                                         
if __name__ == "__main__":
    main()
             