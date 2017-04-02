'''
Created on Mar 10, 2017
'''
from sys import version_info
import glob, os , pprint ,os.path, re, datetime
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
pat_data = "([+]?\d+)\\s(\\S+)\\s+(\\d+?)\\s+(\\d)\\s(\\S+m)\\s(\\S+?g)\\s+(\\S+?m)\\s(\\w)\\s+?(\\S+)\\s(\\d+?.\\d+?)\\s+?(\\d+?\:\\d+?.\\d+?)\\s+?(java)\\s+?"
cr_data = re.compile(pat_data)
pat_jcdata = "(\\S+)\\s(\\S+)\\s(\\S+\\s+:\\s+\\S+)"
cr_jcdata = re.compile(pat_jcdata)
pat_pidln = "\\s+(PID)\\s(USER)\\s+(PR)\\s+(NI)\\s+(VIRT)\\s+(RES)\\s+(SHR)\\s(S)\\s(%CPU)\\s(%MEM)\\s+(TIME+)(.*)"
cr_pidln = re.compile(pat_pidln)
pat_cpu = "(^Cpu\(s\):\\s\\S+),(.*)"
cr_cpu = re.compile(pat_cpu)

                                       
def doprocessjavacore(jfilename,response):
    mydic = {}
    jctime = None
    threadId = None
    threadName = None
    with open(jfilename,'r+') as f: 
                print "Evaluating " + jfilename
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
    with open(filename,'r+') as t:
        for line in t:
            tt = re.match(cr_top,line)
            if tt:
                if tt.group(1) in time:
                    topdata.append(line)
                    for i in range(16):
                        topdata.append(next(t))    
        return topdata
                
def doformattime(jctime):   
    time = []  
    time.append(jctime)
    t = parse(jctime)
    t4 = t + datetime.timedelta(0,1)
    time.append(str(t4.time()))
    t3 = t + datetime.timedelta(0,-1)
    time.append(str(t3.time()))
    t2 = t + datetime.timedelta(0,-2)
    time.append(str(t2.time()))
    t3 = t + datetime.timedelta(0,-2)
    time.append(str(t3.time()))
    return time


def main():
    py3 = version_info[0] > 2 #creates boolean value for test that Python major version > 2
    if py3:
        response = input("Please enter directory where high cpu data resides: ")
    else:
        response = raw_input("Please enter directory where high cpu data resides: ") 
    
    newhtml = os.path.join(response,"HighCPUData.html")
    html = open(newhtml,'w')
    html.write('<html><body><H1>Top 10 process for taken from each Javacore:</H1>')
    
    for jfilename in glob.glob(os.path.join(response,'java*')):
        (mydic,jctime) = doprocessjavacore(jfilename,response)
        topdata = []
        time = []
        if jctime:
            tmptime = doformattime(jctime)
            time.extend(tmptime)
            
        for filename in glob.glob(os.path.join(response,'top*')):
            tmptopdata = doprocesstop(filename, time)
            topdata.extend(tmptopdata) 
        topd = iter(topdata)
        for line in topd:
            tt = re.match(cr_top,line)
            if tt:
                
                toptime = tt.group(1)
                html.write('<br><br><B>%s:</B><br>' % jfilename)
                html.write('<br>%s' %line)
                for i in range(4):
                    cpu = cr_cpu.search(line)
                    if cpu:
                        html.write('<p><b>%s</b> %s' % cpu.group(1) , cpu.group(2))
                    html.write('%s</p>' % (next(topd)))  
            pidln = re.match(cr_pidln,line)      
            if pidln: 
                html.write('<br><table border=\"1\"><tr><td width=\"50\">%s</td>' % pidln.group(1) + '<td width=\"80\">%s</td>' % pidln.group(2) + '<td width=\"80\">%s</td>' % pidln.group(3) + '<td width=\"80\">%s</td>' % pidln.group(4) + '<td width=\"80\">%s</td>' % pidln.group(5) + '<td width=\"50\">%s</td>' % pidln.group(6) + '<td width=\"80\">%s</td>' % pidln.group(7) + '<td width=\"80\">%s</td>' % pidln.group(8) + '<td width=\"80\">%s</td>' % pidln.group(9) + '<td width=\"80\">%s</td>' % pidln.group(10) + '<td width=\"80\">%s</td>' % pidln.group(11) + '<td width=\"120\">%s</td>' % pidln.group(12) + '<td width=\"90\"> Thread ID </td>' + '<td width=\"250\"> Thread Name</td>')
            pt = cr_data.search(line)
            if pt:
                hpid = hex(int(pt.group(1)))
                key = (hpid.upper())
                if key in mydic:
                    html.write('<tr><td width=\"50\">%s</td>' % pt.group(1) + '<td width=\"80\">%s</td>' % pt.group(2) + '<td width=\"80\">%s</td>' % pt.group(3) + '<td width=\"80\">%s</td>' % pt.group(4) + '<td width=\"80\">%s</td>' % pt.group(5) + '<td width=\"50\">%s</td>' % pt.group(6) + '<td width=\"80\">%s</td>' % pt.group(7) + '<td width=\"80\">%s</td>' % pt.group(8) + '<td width=\"80\"><b>%s</b></td>' % pt.group(9) + '<td width=\"80\">%s</td>' % pt.group(10) + '<td width=\"80\">%s</td>' % pt.group(11)+ '<td width=\"120\">%s</td>' % pt.group(12) + '<td width=\"90\"><b>%s<b></td>' % hpid + '<td width=\"350\">%s</td></tr>' % (mydic.get(key,None)))
        html.write('</table>')
                
        
    print "Writing to %s" % newhtml  
    html.write('</body>\n')
    html.write('</html>\n')                                        
if __name__ == "__main__":
    main()
             