'''
Created on Mar 10, 2017
'''
from sys import version_info
import glob, os , pprint ,os.path, re, datetime, webbrowser, subprocess,sys
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
pat_data = "([+]?\d+)\\s(\\S+)\\s+(\\d+?)\\s+(\\d)\\s(\\S+)\\s(\\S+?)\\s+(\\S+?)\\s(\\w)\\s+?(\\S+)\\s(\\d+?.\\d+?)\\s+?(\\d+?\:\\d+?.\\d+?)\\s+?(java)\\s+?"
cr_data = re.compile(pat_data)
pat_jcdata = "(\\S+)\\s(\\S+)\\s(\\S+\\s+:\\s+\\S+)"
cr_jcdata = re.compile(pat_jcdata)
pat_pidln = "\\s+(PID)\\s(USER)\\s+(PR)\\s+(NI)\\s+(VIRT)\\s+(RES)\\s+(SHR)\\s(S)\\s(%CPU)\\s(%MEM)\\s+(TIME+)(.*)"
cr_pidln = re.compile(pat_pidln)
pat_cpu = "(^Cpu\(s\):)\\s(\\S+),(.*)"
cr_cpu = re.compile(pat_cpu)
stkstart = re.compile('3XMTHREADINFO3')
stkend = re.compile('NULL')
tm_pat = "(\\d+):(\\d+):(\\d+)"
cr_tm = re.compile(tm_pat)
                                       
def doprocessjavacore(jfilename,response,jc):
    jc = open(jc,'w')
    jc.write('<html><body><style>pre{display:inline}</style>')
    mydic = {}
    stacks = {}
    jctime = None
    threadId = None
    threadName = None
    with open(jfilename,'r+') as f: 
                print ("Evaluating " + jfilename)
                for line in f:
                    j = cr_datetime.search(line)
                    if j: 
                        jctime = j.group(2)
                        jc.write('<pre>%s</pre><br>' % j.group())
                        continue
                    t = cr_tname.search(line)
                    ta = cr_tname2.search(line)
                    if jctime and t:
                        threadName = t.group(1)
                        jc.write('<h2 id=\"%s\"></h2>' % threadName)
                        jc.write('<pre><b><H3>%s</H3></b></pre>' % (t.group(1)))
                    elif jctime and ta:
                        threadName = ta.group(1)
                        jc.write('<h2 id=\"%s\"></h2>' % threadName)
                        continue
                    n = cr_native.search(line)
                    if jctime and threadName and n:
                            threadId = n.group(1)
                            jckey = (threadId.upper())
                            mydic[jckey] = threadName
                            continue     
                    
                    jc.write('<pre>%s</pre>' % line)
                jc.write('</body><html>')
                return mydic,jctime

def doprocesstop(filename, time, jfilename):
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
    
    newhtml = os.path.join(response,"top.html")
    html = open(newhtml,'w')
    html.write('<html><body><H1>Top 10 process for taken from each Javacore:</H1>')
    
    for jfilename in glob.glob(os.path.join(response,'java*.txt')):
        jc = (jfilename)+ ".html"
        (mydic,jctime) = doprocessjavacore(jfilename,response,jc)
        topdata = []
        time = []
        if jctime:
            tmptime = doformattime(jctime)
            time.extend(tmptime)
        for filename in glob.glob(os.path.join(response,'topdash*')):
            tmptopdata = doprocesstop(filename, time,jfilename)
            if tmptopdata:
                topdata.extend(tmptopdata) 
            else:
                print ("")
                print ("************** Oops ****************")
                print ("Topdash data did not contain a timestamp that matched : " + jfilename)
                print ("************** Oops ****************")
                print ("")
        topd = iter(topdata)
        for line in topd:
            tt = re.match(cr_top,line)
            if tt:
                toptime = tt.group(1)
                html.write('<br><br><B>%s:</B><br><br>' % jfilename)
                html.write('%s<br>' %line)
            cpu = cr_cpu.search(line)
            if cpu:
                html.write('<b>%s</b>' % cpu.group(1)) 
                html.write('<b><span style="color:red">%s</span></b>' % cpu.group(2))
                html.write('%s<br>' % cpu.group(3))
                for i in range(3):
                            html.write('%s<br>' % (next(topd)))     
            pidln = re.match(cr_pidln,line)      
            if pidln: 
                html.write('<br><table border=\"1\"><tr><td width=\"50\">%s</td>' % pidln.group(1) + '<td width=\"80\">%s</td>' % pidln.group(2) + '<td width=\"80\">%s</td>' % pidln.group(3) + '<td width=\"80\">%s</td>' % pidln.group(4) + '<td width=\"80\">%s</td>' % pidln.group(5) + '<td width=\"50\">%s</td>' % pidln.group(6) + '<td width=\"80\">%s</td>' % pidln.group(7) + '<td width=\"80\">%s</td>' % pidln.group(8) + '<td width=\"80\">%s</td>' % pidln.group(9) + '<td width=\"80\">%s</td>' % pidln.group(10) + '<td width=\"80\">%s</td>' % pidln.group(11) + '<td width=\"120\">%s</td>' % pidln.group(12) + '<td width=\"90\"> Thread ID </td>' + '<td width=\"250\"> Thread Name</td>')
            pt = cr_data.search(line)
            if pt:
                hpid = hex(int(pt.group(1)))
                key = (hpid.upper())
                if key in mydic:
                    html.write('<tr><td width=\"50\">%s</td>' % pt.group(1) + '<td width=\"80\">%s</td>' % pt.group(2) + '<td width=\"80\">%s</td>' % pt.group(3) + '<td width=\"80\">%s</td>' % pt.group(4) + '<td width=\"80\">%s</td>' % pt.group(5) + '<td width=\"50\">%s</td>' % pt.group(6) + '<td width=\"80\">%s</td>' % pt.group(7) + '<td width=\"80\">%s</td>' % pt.group(8) + '<td width=\"80\"><b>%s</b></td>' % pt.group(9) + '<td width=\"80\">%s</td>' % pt.group(10) + '<td width=\"80\">%s</td>' % pt.group(11)+ '<td width=\"120\">%s</td>' % pt.group(12) + '<td width=\"90\"><b>%s<b></td>' % hpid + '<td width=\"350\"><a href=\"%s#%s" target="frame_jc">%s</a></td></tr>' % (jc.rstrip('\\') , (mydic.get(key,None)) , (mydic.get(key,None))))
                
        html.write('</table>')
                
    hcpufile = os.path.join(response,"HighCpuData.html")
    hcpu = open(hcpufile,'w')  
    hcpu.write('<html><frameset rows="400px,*"><frame src="top.html"><frameset rows="900px,*"><frame name="frame_jc"></frameset></frameset></html>')
      
    print ("Writing to %s" % newhtml)
    print ("----------------------------------------------------------------------------------")
    print (" Please open HighCpuData.html to review the top 10 java process for each javacore")
    html.write('</body>\n')
    html.write('</html>\n') 
    if sys.platform=='win32':
        print ("Opening HighCpuData.html in browser")
        os.startfile(hcpufile)
    elif sys.platform=='darwin':
        print ("Opening HighCpuData.html in browser")
        subprocess.Popen(['open', hcpufile])
    else:
        try:
            subprocess.Popen(['xdg-open', hcpufile])
            print ("Opening HighCpuData.html in browser")
        except OSError:
            print 'Please open a browser on: '+ hcpufile
        #webbrowser.open_new('file://hcpufile')
    
                                           
if __name__ == "__main__":
    main()
             