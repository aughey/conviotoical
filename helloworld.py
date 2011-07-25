from google.appengine.api import urlfetch
from xml.dom import minidom
import re

url = 'https://secure3.convio.net/nmss/site/CROrgEventAPI?method=getMonthEvents&v=1.0&api_key=ZedRa4uc&response_format=xml&month=7&year=2011&interests=2623'

result = urlfetch.fetch(url=url, headers={'use_intranet': 'yes'})

dom = minidom.parseString(result.content)

print 'Content-Type: text/plain'
print ''
print 'BEGIN:VCALENDAR'
print 'VERSION:2.0'

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
  return "%04d%02d%02dT%02d%02d00" % (year,month,day,hour,minute)


for event in getChildren(getChild(dom,"getMonthEventsResponse"),'event'):
  name = getChild(event,'name')
  print 'BEGIN:VEVENT'
  print "SUMMARY:%s" % getText(name.childNodes)
  eventdate = getChild(event,'eventDate')
  start = parseTime(getText(getChild(eventdate,'startDate')),getText(getChild(eventdate,'startTime')))
  enddate = getChild(eventdate,'endDate')
  if(enddate == None):
    enddate = getChild(eventdate,'startDate')

  end = parseTime(getText(enddate),getText(getChild(eventdate,'endTime')))
  print "DTSTART;TZID=US-Central:" + start
  print "DTEND;TZID=US-Central:" + end
  print 'END:VEVENT'

print 'END:VCALENDAR'
