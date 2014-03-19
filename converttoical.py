import webapp2

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
	data = data.content
	memcache.set(url,data,60 * 60) # Cache for 1 hour
	return data

def lf(data):
	return data + "\n"

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
  offset = int(dates[3])

  res = datetime.datetime(year,month,day,hour,minute)
  res = res + datetime.timedelta(hours=offset)

  #return "%04d%02d%02dT%02d%02d00" % (year,month,day,hour,minute)
  return res.strftime("%Y%m%dT%H%M%SZ")


def printevents(response,month,year,interests):
  url = 'https://secure3.convio.net/nmss/site/CROrgEventAPI?method=getMonthEvents&v=1.0&api_key=ZedRa4uc&response_format=xml&month=%d&year=%d&interests=%s' % (month,year,interests)

  response.write(lf("COMMENT:Result of date fetch %d-%d" % (year,month)))
  response.write(lf("COMMENT:Url is %s" % url))

  result = getUrl(url)

  dom = minidom.parseString(result)

  for event in getChildren(getChild(dom,"getMonthEventsResponse"),'event'):
	name = getChild(event,'name')
	response.write(lf('BEGIN:VEVENT'))
	response.write(lf("SUMMARY:%s " % (getText(name))))
	response.write(lf("DESCRIPTION:%s <a href=\"%s\">More Information</a>" % (getText(name),getText(getChild(event,'eventUrl')))))
	response.write(lf("PRODID:%s" % getText(getChild(event,'eventUrl'))))
	response.write(lf("URL:%s" % getText(getChild(event,'eventUrl'))))
	eventdate = getChild(event,'eventDate')
	start = parseTime(getText(getChild(eventdate,'startDate')),getText(getChild(eventdate,'startTime')))
	enddate = getChild(eventdate,'endDate')
	if(enddate == None):
	  enddate = getChild(eventdate,'startDate')

	end = parseTime(getText(enddate),getText(getChild(eventdate,'endTime')))
	response.write(lf("DTSTART:" + start))
	response.write(lf("DTEND:" + end))
	response.write(lf('END:VEVENT'))

def println(self,line):
	self.write(line + "\n");

#google.appengine.ext.webapp2.println = println

class MainPage(webapp2.RequestHandler):
	def get(self):
		response = self.response

		response.headers['Content-Type'] = 'text/plain'

		response.write(lf('BEGIN:VCALENDAR'))
		response.write(lf('VERSION:2.0'))

		interests = self.request.get('interests')
		if not interests:
			interests = 2623

		#interests = 2580

		now = datetime.datetime.now();
		for monthoffset in range(-3,12):
		  toprint = now + datetime.timedelta(days=monthoffset * 30)
		  printevents(response,toprint.month,toprint.year,interests)

		response.write(lf('END:VCALENDAR'))


application = webapp2.WSGIApplication([
	('/', MainPage),
], debug=True)
