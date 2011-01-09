


class Monitor:
    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.readfp(open('config.txt'))
        self.agent = Agent('config.txt')
    
    def add_task(self, name, repeat):
        theTask = None
        for tt in tasks.TaskTypes:
            if (tt.taskName == name):
                theTask = tt(self.agent)
        
        if theTask == None:
            print "Error -- didn't know what task to do"
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
    monitor.add_task("NoOp", 0)

if __name__ == "__main__":
    main()
