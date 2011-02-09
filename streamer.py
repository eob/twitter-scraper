import tweepy
import json
import sys

class Streamer(object):
    def __init__(self, qid, agent, username, password, api=None):
        self.api = api or tweepy.API()
        self.agent = agent
        self.qid = qid
        self.filter = []
        self.stream = tweepy.Stream(username, password, self)

    def start(self, query=None):
        print "Stream %s starting" % self.qid
        self.filter = query
        if (query == None):
            self.stream.sample(async=True)
        else:
            self.stream.filter(None, self.filter, async=True)
        
    def stop(self):
        print "Stream %s stopping" % self.qid
        self.stream.disconnect()
        
    def on_data(self, data):
        """Called when raw data is received from connection.

        Override this method if you wish to manually handle
        the stream data. Return False to stop stream and close connection.
        """
        try:
            if 'in_reply_to_status_id' in data:
                jsdata = json.loads(data)
                # status = Status.parse(self.api, jsdata)
                if self.on_status(jsdata) is False:
                    return False
            elif 'delete' in data:
                delete = json.loads(data)['delete']['status']
                if self.on_delete(delete['id'], delete['user_id']) is False:
                    return False
            elif 'limit' in data:
                if self.on_limit(json.loads(data)['limit']['track']) is False:
                    return False
        except Exception as ex:
            print "Unexpected error:", sys.exc_info()[0]
            print ex
            print ex.args
            
    def on_status(self, status):
        """Called when a new status arrives"""
        self.agent.receive_tweet(status)
        return

    def on_delete(self, status_id, user_id):
        """Called when a delete notice arrives for a status"""
        print "DEL"
        return

    def on_limit(self, track):
        """Called when a limitation notice arrvies"""
        print "Limit Notice. %s tweets have been dropped since start of connection." % str(track)
        return

    def on_error(self, status_code):
        """Called when a non-200 status code is returned"""
        print "ERROR %s" % str(status_code)
        return False

    def on_timeout(self):
        """Called when stream connection times out"""
        print "TIMEOUT"
        return
        

if __name__ == "__main__":
    class R:
        def receive_tweet(self, status):
            print str(status)
    r = R()
    s = Streamer(0, r, 'foobar005', 'foobar')
    s.start(['twitter'])
