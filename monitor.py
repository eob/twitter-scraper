from optparse import OptionParser
import ConfigParser
from agent import Agent
from tasks import tasks
from database import database
import pickle
import base64

class Monitor:
    def __init__(self, configFile):
        config = ConfigParser.ConfigParser()
        config.readfp(open(configFile))
        self.agent = Agent(configFile)
    
    def list_tasks(self):
        print "============================================================================"
        print "| TASKS                                                                    |"
        print "============================================================================"
        sql = "SELECT tid,task,after,reschedule,delta,args FROM tasks WHERE complete=0 ORDER BY after;"
        result = self.agent.db.query(sql)
        print '| {0:3} | {1:10} | {2:29} | {3:12} | {4:6} |'.format("TID", "Task", "After", "Reschedule?", "Delta")
        print "----------------------------------------------------------------------------"
        for row in result:
            print '| {0:3} | {1:10} | {2:29} | {3:12d} | {4:6} |'.format(row[0], row[1], row[2], row[3], row[4])
            args = ""
            if (len(row[5]) > 0):
                args = str(pickle.loads(base64.b64decode(row[5])))
            print '| args: {0:66} |'.format(args)
        print "----------------------------------------------------------------------------"
    
    def add_task(self, name, repeat, delta, args=[]):
        print "Adding Task"
        theTask = None
        for tt in tasks.TaskTypes:
            if (tt.taskName == name):
                theTask = tt(self.agent, args)
        
        if theTask == None:
            print "Error -- didn't know what task to do"
            print "Valid task types are: " + ", ".join(map(lambda x : x.taskName, tasks.TaskTypes))
        else:
            if (repeat == 0):
              theTask.repeats = False
            else:
                theTask.repeats = True
                theTask.delta = repeat
            theTask.schedule()

def main():
    monitor = Monitor("config.txt")
    # task = tasks.Task(agent.db)
    # task.schedule(False)
    parser = OptionParser()
    parser.add_option("-t", "--tasks", dest="tasks", help="peroform a TASK action", metavar="TASK")
    (options, args) = parser.parse_args()
    print "Options " + str(options)
    print "Args " + str(args)
    print ""
    if options.tasks:
        if options.tasks == "list":
            monitor.list_tasks()
        elif options.tasks == "add":
            if len(args) < 3:
                print "Usage: --add task repeat? delta"
                print "Valid task types are: " + ", ".join(map(lambda x : x.taskName, tasks.TaskTypes))
            else:
                if (len(args) < 4):
                    monitor.add_task(args[0], int(args[1]), int(args[2])) 
                else:
                    monitor.add_task(args[0], int(args[1]), int(args[2]), args[3:]) 
                    
if __name__ == "__main__":
   main()
