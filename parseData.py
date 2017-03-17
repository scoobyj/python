'''
Created on Mar 10, 2017
'''
from sys import version_info
from itertools import islice
import glob, os , pprint ,os.path, re

# Patterns
pat_datetime = "^1TIDATETIME\\s+Date:\\s+(\\S+) at (\\S+)"
cr_datetime = re.compile(pat_datetime)
pat_native = "^3XMTHREADINFO1\\s+\(native thread ID:(\\S+),(.*)"
cr_native = re.compile(pat_native)
pat_tname = "^3XMTHREADINFO\\s+\\S(\\S+\\s\\S\\s\\S+)\\S(.*)"



cr_tname = re.compile(pat_tname)
pat_top = "^top\\s\\S\\s(\\S+)(.*)"
cr_top = re.compile(pat_top)
pat_desc = "\\s(\\S+)(.*) SHR S (\\S+)(.*)"
cr_desc = re.compile(pat_desc)
pat_time = "(\\S+)\\s(\\S+)\\s(\\S+\\s:\\s\\S+)"
cr_time = re.compile(pat_time)
pat_data = "(\\d+).*?[+-]?\\d*\\.\\d+(?![-+0-9\\.]).*?([+-]?\\d*\\.\\d+)(?![-+0-9\\.]).*?(java)\\s+"
cr_data = re.compile(pat_data)
pat_jcdata = "(\\S+)\\s(\\S+)\\s(\\S+\\s+:\\s+\\S+)"
cr_jcdata = re.compile(pat_jcdata)
                                       
def doprocessjavacore(filename):
    jcdata = []  
    jctime = None
    threadId = None
    threadName = None
    with open(filename) as f: 
                for line in f:
                    j = cr_datetime.search(line)
                    if j: 
                        jctime = j.group(2)
                        continue

                    t = cr_tname.search(line)
                    if t:
                        threadName = t.group(1)
                        continue
                    n = cr_native.search(line)
                    if jctime and threadName and n:
                        threadId = n.group(1)
                        jcdata.append(jctime + " " + threadId + " " +  threadName)
                return jcdata,jctime

def doprocesstop(filename, jctime):
    topdata = []   
    with open(filename) as t:
        for line in t:
            tt = re.match(cr_top,line)
            if tt:
                if jctime == tt.group(1):
                    topdata.append(line)
                    for i in range(16):
                        topdata.append(t.next())
        return topdata
                
                       


def main():
    py3 = version_info[0] > 2 #creates boolean value for test that Python major version > 2

    if py3:
        response = input("Please enter directory where high cpu data resides: ")
    else:
        response = raw_input("Please enter directory where high cpu data resides: ") 
    alljcdata = []
    for filename in glob.glob(os.path.join(response,'java*')):
        (filejcdata, jctime) = doprocessjavacore(filename)
        alljcdata.extend(filejcdata)
        topdata = []
        for filename in glob.glob(os.path.join(response,'top*')):
            tmptopdata = doprocesstop(filename, jctime)
            topdata.extend(tmptopdata) 
    print ("ALL JCDATA\n%s\n" % "\n".join(alljcdata))
    for line in topdata:
        tt = re.match(cr_top,line)
        if tt:
            toptime = tt.group(1)
        pt = cr_data.search(line)
        if pt:
                hpid = hex(int(pt.group(1)))
                hpid = hpid.upper()
                cpu = pt.group(2)
                for line in alljcdata:
                    jc = cr_jcdata.search(line)
                    if jc:
                        jctid = jc.group(2)
                        jctid = jctid.upper()
                        if jctid == hpid and toptime == jc.group(1):
                                print ( "Time:  " +  toptime +  "  cpu:  " + cpu +"       ThreadName :  " + jc.group(3))
                         #### I got a bug and I cant figure it out   
                                
                                         
if __name__ == "__main__":
    main()
             
