import time, datetime
import re
from scrapers import new_york
import datetime
import cPickle as pickle
import base64
from english import English
import feedparser

class Task(object):
    taskName = "NoOp"

    def __init__(self, agent, args):
        self.agent = agent
        self.args = args
        self.name = Task.taskName
        self.reschedules = False
        self.delta = 0
        self.tid = 0
        self.db = self.agent.db
        
    def schedule(self, add_delta = True):
        print "Scheduling task" 
        sql = "INSERT INTO tasks (task, after, reschedule, delta, args) VALUES (?,?,?,?,?);"
        if add_delta:            
            thedate = datetime.datetime.now() + datetime.timedelta(seconds=self.delta)
        else:
            thedate = datetime.datetime.now()
        params = [self.name, thedate, self.reschedules, self.delta, base64.b64encode(pickle.dumps(self.args))]
        cur = self.db.query(sql, params)
        cur.close()
        self.db.commit()

    def schedule_if_none_exist(self):
        print "Scheduling task if none exists"
        sql = "SELECT tid FROM tasks WHERE complete = 0 AND task = ?"
        if not self.db.bool_query(sql, (self.name)):
            self.schedule(self.db)

    def complete(self, allow_reschedule=True):
        print "Completing task"
        sql = "UPDATE tasks SET complete = ?, completed_on = ? WHERE tid = ?"
        params = [1, datetime.datetime.now(), self.tid]
        cur = self.db.query(sql, params)
        cur.close()
        self.db.commit()
        print "Completed"
        # Reschedule
        if allow_reschedule and self.reschedules:
            self.schedule(self.db)
            
    def execute(self):
        print "No-Op"
    
    
class ScrapeNycTask(Task):
    taskName = "ScrapeNyc"
    
    def __init__(self, agent, args):
        """
        Scrape the NYC.com events table and
        load new events for the coming 7 days into the database
        """
        super(ScrapeNycTask,self).__init__(agent, args)
        self.name = ScrapeNycTask.taskName
        self.reschedules = True
        self.delta = delta
        self.tid = 0
    
    def execute(self):
        print "Scraping NYC.com"
        events = new_york.fetch_events()
        for event in events:
            # We use title+time+source as the unique identifier
            if not self.db.bool_query(['events', 'eid'], {'title':event['title'], 'event_time':event['event_time'], 'source':event['source']}):
                self.db.safe_insert('events', event)

class CreateQueriesFromEventsTask(Task):
    taskName = "EventsToQueries"
    
    def __init__(self, agent, args):
        """
        Find events with:
          * ticket price > $10
          * title less than 40 characters
          * no query records in the database
        and create query records for them
        """
        super(CreateQueriesFromEventsTask,self).__init__(agent, args)
        self.name = CreateQueriesFromEventsTask.taskName
        self.reschedules = True
        self.delta = delta
        self.tid = 0

    def execute(self):
        print "CreateEventQueries"
        sql = 'select eid,title,venue,source,event_time from events where (select count(*) from queries where queries.eid=events.eid)=0 and events.ticket_price > 10 and length(events.title) < 40;'
        cur = self.db.query(sql)
        for row in cur:
            eid = row[0]
            title = row[1]
            venue = row[2]
            date = row[4]
            start = datetime.datetime.now()
            end = date + datetime.timedelta(days=2)
            
            self.db.insert('queries', {
                'eid':eid,
                'query':title,
                'start_date':start,
                'stop_date':stop
            })
            self.db.commit()

            self.db.insert('queries', {
                'eid':eid,
                'query':venue,
                'start_date':start,
                'stop_date':stop
            })
            self.db.commit()

        cur.close()

class ScrapeUserTask(Task):
    taskName = "ScrapeUser"

    def __init__(self, agent, args):
        super(ScrapeUserTask, self).__init__(agent, args)
        self.name = ScrapeUserTask.taskName
        self.user = self.args[0]
        
        # For keeping track of pulling in others in the social network
        # self.radius = 0
        # if len(self.args) > 1:
        #     self.radius = int(self.args[1])
        
    def execute(self):
        # Pull down all the tweets after lastKnownTweet              
        tweets = getNewTwets()
        saveTweets(tweets)
  
    def getNewTweets(self):
        lastTime = self.db.lastTweetFrom(self.user)
        if lastTime == 0:
            tweets = [] # get all tweets
        else:
            tweets = [] # get tweets since last
        self.saveTweets(tweets)
         
    def saveTweets(self, tweets):
        pass

class StartStreamTask(Task):
    taskName = "StartStream"

    def __init__(self, agent, args):
        super(StartStreamTask,self).__init__(agent, args)
        self.name = StartStreamTask.taskName
        self.reschedules = False

    def execute(self):
        self.agent.streamSampler.start()

class StopStreamTask(Task):
    taskName = "StopStream"

    def __init__(self, agent, args):
        super(StopStreamTask,self).__init__(agent, args)
        self.name = StopStreamTask.taskName
        self.reschedules = False

    def execute(self):
        self.agent.streamSampler.stop()

class StartFilterStreamTask(Task):
    taskName = "StartFilterStream"

    def __init__(self, agent, args):
        super(StartFilterStreamTask,self).__init__(agent, args)
        self.name = StartFilterStreamTask.taskName
        self.reschedules = False

    def execute(self):
        self.agent.filterSampler.start(self.args)

class StopFilterStreamTask(Task):
    taskName = "StopFilterStream"

    def __init__(self, agent, args):
        super(StopFilterStreamTask,self).__init__(agent, args)
        self.name = StopFilterStreamTask.taskName
        self.reschedules = False

    def execute(self):
        self.agent.filterSampler.stop()

class SaveTweetsTask(Task):
    taskName = "SaveTweets"
    
    def __init__(self, agent, args):
        super(SaveTweetsTask,self).__init__(agent, args)
        self.name = SaveTweetsTask.taskName
        self.reschedules = True

    def execute(self):
        self.agent.save_tweets()

class DumpTweetsTask(Task):
   taskName = "DumpTweets"

   def __init__(self,agent,args):
       super(DumpTweetsTask,self).__init__(agent,args)
       self.name = DumpTweetsTask.taskName

   def execute(self):
       if "english" not in self.agent.blackboard:
           english = English()
           self.agent.stash("english", english)
       english = self.agent.fetch("english")
       tweets = self.agent.tweet_cache
       self.agent.tweet_cache = []
       for tweet in tweets:
           # Only dump English tweets. 
           # XXX - Rest of world: remove this if statement
           if english.is_english(tweet["text"]):
               print tweet["text"]

class FileDumperTask(Task):
    taskName = "FileDumper"

    def __init__(self,agent,args):
        super(FileDumperTask,self).__init__(agent,args)
        self.name = FileDumperTask.taskName
        if len(args) > 0:
            self.filename = args[0]
        else:
            self.filename = None
        
    def execute(self):
        if "english" not in self.agent.blackboard:
            english = English()
            self.agent.stash("english",english)
        english = self.agent.fetch("english")
        tweets = self.agent.tweet_cache
        self.agent.tweet_cache = []
        if self.filename != None:
            f = open(self.filename, "a") 
        dayFiles = {}
        
        for tweet in tweets:
            if english.is_english(tweet["text"]):
                if self.filename != None:
                    fOut = f
                else:
                    dateName = "tweets-%i-%i-%i" % (tweet.created_at.year, tweet.created_at.month, tweet.created_at.day)
                    if dateName not in dayFiles:
                        dayFiles[dateName] = open(dateName, "a")
                    fOut = dayFiles[dateName]
                self.write_tweet(fOut,tweet)
        
        if self.filename != None:
            f.close()
        for ff in dayFiles:
            ff.close()

    def write_tweet(self,f,tweet):
        f.write(tweet + "\n")

class PullRandomUsersTask(Task):
    taskName = "PullRandomUsers"

    def __init__(self, agent, args):
        super(PullRandomUsersTask,self).__init__(agent, args)
        self.name = PullRandomUsersTask.taskName
        self.reschedules = True
        self.num_users = args[0]
        self.num_tweets = args[1]

    def execute(self):
        sql = "SELECT twitter_name, count(tid) AS cnt FROM tweets,people WEHRE tweets.pid = people.pid AND cnt = 1 ORDER BY rand() LIMIT %i" % self.num_users
        res = self.db.query(sql)
        for row in res:
            tid = row[0]
            # Schedule a new task
            task = ScrapeUserTask(self.agent, [tid, self.num_tweets])
            task.reschedules = False
            task.delta = 0
            task.schedule()

class PullFeedTask(Task):
    taskName = "PullFeed"

    def __init__(self,agent,args):
        super(PullFeedTask,self).__init__(agent,args)
        self.name = PullFeedTask.taskName
        self.reschedules = False
        self.feed = args[0]

    def execute(self):
        data = feedparser.parse(self.feed)
        if 'entries' in data:
            for entry in data['entries']:
                self.add_entry(entry) 

    def add_entry(self, entry):
        vals = {
                'feed':self.feed,
                'posted':time.mktime(entry.updated_parsed),
                'title':entry.title,
                'link':str(entry.link),
                'summary':re.sub(r"<[^>]+>", "", entry.summary).strip(),
                'tags':"\t".join([tag.term for tag in entry.tags])
        }
        self.db.safe_insert("feeds",vals)

class DieTask(Task):
    taskName = "Die"

    def __init__(self,agent,args):
        super(DieTask,self).__init__(agent, args)
        self.name = DieTask.taskName

    def execute(self):
        print "Goodbye, world"
        self.agent.filterSampler.stop()
        self.agent.streamSampler.stop()
        self.agent.expire = True
        
# This defines which tasks the monitor.py script will support.
TaskTypes = [   Task, 
                ScrapeUserTask,
                StartStreamTask,
                StopStreamTask,
                StartFilterStreamTask,
                StopFilterStreamTask,
                SaveTweetsTask,
                PullRandomUsersTask,
                DumpTweetsTask,
                DieTask,
                FileDumperTask,
                PullFeedTask
            ]
