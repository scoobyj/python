'''
Created on Mar 10, 2017
'''
from sys import version_info
from itertools import islice, izip
import glob, os , pprint ,os.path, re, datetime
import itertools
from dateutil.parser import parse


# Patterns
pat_datetime = "^1TIDATETIME\\s+Date:\\s+(\\S+) at (\\S+)"
cr_datetime = re.compile(pat_datetime)
pat_native = "^3XMTHREADINFO1\\s+\(native thread ID:(\\S+),(.*)"
cr_native = re.compile(pat_native)
pat_tname = "^3XMTHREADINFO\\s+\"(.*)\"(.*)"
cr_tname = re.compile(pat_tname)
pat_tname2 = "^3XMTHREADINFO\\s+(A.*)"
cr_tname2 = re.compile(pat_tname2)
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
    mydic = {}
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
                    ta = cr_tname2.search(line)
                    if jctime and t:
                        threadName = t.group(1)
                    elif jctime and ta:
                        threadName = ta.group(1)
                        continue
                    n = cr_native.search(line)
                    if jctime and threadName and n:
                            threadId = n.group(1)
                            jckey = (threadId.upper())
                            mydic[jckey] = threadName
                            continue
                    
                return mydic,jctime

def doprocesstop(filename, time):
    topdata = []   
    with open(filename) as t:
        for line in t:
            tt = re.match(cr_top,line)
            if tt:
                if tt.group(1) in time:
                    topdata.append(line)
                    for i in range(16):
                        topdata.append(t.next())
        return topdata
                
def doformattime(jctime):    ##### need better way to do this
    time = []  
    time.append(jctime)
    t = parse(jctime)
    tt = t + datetime.timedelta(0,1)
    time.append(str(tt.time()))
    ttt = t + datetime.timedelta(0,-1)
    time.append(str(ttt.time()))
    return time
    


def main():
    py3 = version_info[0] > 2 #creates boolean value for test that Python major version > 2

    if py3:
        response = input("Please enter directory where high cpu data resides: ")
    else:
        response = raw_input("Please enter directory where high cpu data resides: ") 
    for filename in glob.glob(os.path.join(response,'java*')):
        (mydic,jctime) = doprocessjavacore(filename)
        topdata = []
        time = []
        tmptime = doformattime(jctime)
        time.extend(tmptime)
        for filename in glob.glob(os.path.join(response,'top*')):
            tmptopdata = doprocesstop(filename, time)
            topdata.extend(tmptopdata) 
        #print ("ALL JCDATA\n%s\n" % "\n".join(alljcdata))
   # print ("ALL JCDATA\n%s\n" % "\n".join(alljcdata))
    #print ("MYDIC\n%s\n" % "\n".join(mydic))
        for line in topdata:
            tt = re.match(cr_top,line)
            if tt:
                toptime = tt.group(1)
                print line.rstrip('\n')
                
                
                # got to be an easier way to do this.... 
            if 'Tasks' in line: print line.rstrip('\n')
            if 'Cpu' in line: print line.rstrip('\n')
            if 'Mem' in line: print line.rstrip('\n')
            if 'Swap' in line: print line.rstrip('\n')
            if 'PID' in line: print line.rstrip('\n') + ("ThreadName")

            pt = cr_data.search(line)
            if pt:
                hpid = hex(int(pt.group(1)))
                key = (hpid.upper())
                if key in mydic:
                    print (line.rstrip('\n') + (mydic.get(key,None)))
                        
                                         
if __name__ == "__main__":
    main()
             