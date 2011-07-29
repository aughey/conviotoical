from google.appengine.api import urlfetch
from google.appengine.api import memcache
from xml.dom import minidom
import re
import datetime

def getUrl(url):
  cached = memcache.get(url)
  if cached:
    return cached
  else:
    data = urlfetch.fetch(url=url, headers={'use_intranet': 'yes'})
    memcache.set(url,data,60 * 60) # Cache for 1 hour
    return data

def getChildren(element, childname):
  return [item for item in element.getElementsByTagName(childname) if item.parentNode == element]

def getChild(element,childname):
  children = getChildren(element,childname)
  if(len(children) > 0):
    return children[0]
  else:
    return None


def getText(nodelist):
  if(nodelist == None):
    return None

  if not isinstance(nodelist, minidom.NodeList):
    nodelist = nodelist.childNodes

  for node in nodelist:
    if node.nodeType == node.TEXT_NODE:
      return node.data

def parseTime(date,time):
  dates =  re.findall('\d+',date)
  if time == None:
    times = [0,0,0,0,0]
  else:
    times =  re.findall('\d+',time)
  year = int(dates[0])
  month = int(dates[1])
  day = int(dates[2])
  hour = int(times[0])
  minute = int(times[1])
  offset = int(times[4])

  res = datetime.datetime(year,month,day,hour,minute)
  toprint = now + datetime.timedelta(days=monthoffset * 30)
  res = res - datetime.timedelta(hours=offset)

  #return "%04d%02d%02dT%02d%02d00" % (year,month,day,hour,minute)
  return res.strftime("%Y%m%dT%H%M%SZ")


def printevents(month,year):
  url = 'https://secure3.convio.net/nmss/site/CROrgEventAPI?method=getMonthEvents&v=1.0&api_key=ZedRa4uc&response_format=xml&month=%d&year=%d&interests=2623' % (month,year)

  print "COMMENT:Result of date fetch %d-%d" % (year,month)
  print "COMMENT:Url is %s" % url

  result = getUrl(url)

  dom = minidom.parseString(result.content)

  for event in getChildren(getChild(dom,"getMonthEventsResponse"),'event'):
    name = getChild(event,'name')
    print 'BEGIN:VEVENT'
    print "SUMMARY:%s" % getText(name)
    print "URL:%s" % getText(getChild(event,'eventUrl'))
    eventdate = getChild(event,'eventDate')
    start = parseTime(getText(getChild(eventdate,'startDate')),getText(getChild(eventdate,'startTime')))
    enddate = getChild(eventdate,'endDate')
    if(enddate == None):
      enddate = getChild(eventdate,'startDate')

    end = parseTime(getText(enddate),getText(getChild(eventdate,'endTime')))
    print "DTSTART:" + start
    print "DTEND:" + end
    print 'END:VEVENT'



print 'Content-Type: text/plain'
print ''
print 'BEGIN:VCALENDAR'
print 'VERSION:2.0'

now = datetime.datetime.now();
for monthoffset in range(-3,12):
  toprint = now + datetime.timedelta(days=monthoffset * 30)
  printevents(toprint.month,toprint.year)

print 'END:VCALENDAR'
