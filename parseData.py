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
                                       
def doprocessjavacore(filename):
    with open(filename) as f:
                for line in f:
                    j = cr_datetime.search(line)
                    if j:
                       global jctime
                       jctime = j.group(2)
                    n = cr_native.search(line)
                    if n:
                        global threadId
                        threadId = n.group(1)
                    t = cr_tname.search(line)
                    if t:
                        global threadName
                        threadName = t.group(1)
                        jcdata = [jctime,threadId,threadName]
                        print(jcdata)  

def doprocesstop(filename):
    with open(filename) as t:
            for line in t:
                tt = cr_top.search(line)
                if tt:
                    toptime = tt.group(1)
                    topdata =[]
                    for i in range(16):
                        topdata.append(t.next())
                    if toptime == jctime:   # This is comparing to the last timestamp from jc instead of each
                        print (''.join(topdata))
                        for line in topdata[6:]:
                            data = cr_topd.search(line)
                            if data:
                                pid = int(data.group(1))
                                hpid = hex(pid)
                                print(pid,hpid)
                                # Just a test
                    
                       


def main():
    py3 = version_info[0] > 2 #creates boolean value for test that Python major version > 2

    if py3:
        response = input("Please enter directory where high cpu data resides: ")
    else:
        response = raw_input("Please enter directory where high cpu data resides: ")    
  
    for filename in glob.glob(os.path.join(response,'java*')):
          doprocessjavacore(filename)                                                    
                              
    for filename in glob.glob(os.path.join(response,'top*')):
            doprocesstop(filename)
                        
                                         
if __name__ == "__main__":
    main()
             