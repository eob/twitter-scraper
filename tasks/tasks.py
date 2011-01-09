from scrapers import new_york
import datetime

class Task:
    taskName = "NoOp"

    def __init__(self, agent):
        self.agent = agent
        self.name = Task.taskName
        self.reschedules = False
        self.delta = 0
        self.tid = 0
        self.db = self.agent.db
        
    def schedule(self, add_delta = True):
        sql = "INSERT INTO tasks (task, after, reschedule, delta) VALUES (?,?,?,?);"
        if add_delta:            
            thedate = datetime.datetime.now() + datetime.timedelta(seconds=self.delta)
        else:
            thedate = datetime.datetime.now()
        params = [self.name, thedate, self.reschedules, self.delta]
        cur = self.db.query(sql, params)
        cur.close()
        self.db.commit()

    def schedule_if_none_exist(self):
        sql = "SELECT tid FROM tasks WHERE complete = 0 AND task = ?"
        if not self.db.bool_query(sql, (self.name)):
            self.schedule(self.db)

    def complete(self, allow_reschedule=True):
        print "Com"
        sql = "UPDATE tasks SET complete = ?, completed_on = ? WHERE tid = ?"
        params = [1, str(datetime.datetime.now), self.tid]
        cur = self.db.query(sql, params)
        cur.close()
        self.db.commit()

        # Reschedule
        if allow_reschedule and self.reschedules:
            self.schedule(self.db)
            
    def execute(self):
        print "No-Op"
    
    
class ScrapeNycTask(Task):
    taskName = "ScrapeNyc"
    
    def __init__(self, db, delta):
        """
        Scrape the NYC.com events table and
        load new events for the coming 7 days into the database
        """
        super(ScrapeNycTask,self).__init__(db)
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
    
    def __init__(self, db, delta):
        """
        Find events with:
          * ticket price > $10
          * title less than 40 characters
          * no query records in the database
        and create query records for them
        """
        super(CreateQueriesFromEventsTask,self).__init__(db)
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

class SaveTweetsTask(Task):
    taskName = "SaveTweets"
    
    def __init__(self, db, delta):
        super(SaveTweetsTask,self).__init__(db)
        self.name = SaveTweetsTask.taskName
        self.reschedules = True
        self.delta = delta
        self.tid = 0

    def execute(self):
        tweets = self.agent.fetch("tweets")
        agent.destroy("tweets")
        print "[%s] Saving %d Tweets" % (str(datetime.datetime.now()), len(tweets))
        for tweet in tweets:
            print tweet

TaskTypes = [Task]