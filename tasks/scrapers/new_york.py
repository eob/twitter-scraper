from BeautifulSoup import BeautifulSoup
import re
import urllib2
import os
import subprocess
import datetime 
import os.path
import pytz

def fetch_events():
    """
    Returns events in the database schema format
    [{
        'title':'foo',
        'venue':'foo',
        'address1':'foo',
        'address2':'foo',
        'description':'foo',
        'url':'foo',
        'event_time':'foo',
        'ticket_price':'foo'
    }]
    
    Unfortunately, Ruby has much better HTML extraction libraries, so this script is
    going to invoke a ruby script and read its output. 
    
    Yeah. Duct tape.
    """
    filename = "new_york.csv"
    filename = os.path.join(os.path.dirname(__file__), filename)
    scriptname = "new_york.rb"
    scriptname = os.path.join(os.path.dirname(__file__), scriptname)
    if os.path.exists(filename):
        os.remove(filename)
    now = datetime.datetime.now()
    then1 = now + datetime.timedelta(days = 3)
    then2 = now + datetime.timedelta(days = 5)
    start = then1.strftime("%m/%d/%Y")
    stop = then2.strftime("%m/%d/%Y")
    print "Calling Ruby"
    subprocess.call(['ruby', scriptname, filename, start, stop])
    print "Called Ruby"
    f = open(filename)
    fmt = "%b %d, %I:%M %p"
    events = []
    for line in f:
        (title, venue, address1, address2, date, description, url, cost) = line.strip().split('\t')
        cost = float(cost)
        parsed = datetime.datetime.strptime(date, fmt)
        year = 2010
        if parsed.month < datetime.datetime.now().month:
            year += 1
        date = parsed.replace(year = year)
        
        local = pytz.timezone ("America/New_York")
        local_dt = date.replace (tzinfo = local)
        utc_dt = local_dt.astimezone (pytz.utc)        
        
        events.append({
            'title':title,
            'venue':venue,
            'address1':address1,
            'address2':address2,
            'description':description,
            'url':url,
            'event_time':utc_dt,
            'ticket_price':cost,
            'source':'nyc.com'
        })
    return events
