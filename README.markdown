Twitter Scraper
===============

This is a light-weight agent-based framework to help you schedule a workflow of
scraping tasks, mainly focused on Twitter.

Running
------- 

- Fill in **config.txt** with your own values.
- Next run the agent:

	python agent.py

This agent runs in the backround and does things based on the tasks that are 
assigned to it. You can schedule tasks using another command line took, `monitor.py`.

Recipes (Quick Start)
----------------------

To sample from the twitter stream

	python monitor.py --tasks add StartStream 
	
To pull down tasks for a `@edwardbenson`
	
	python monitor.py --tasks add ScrapeUser 0 0 @edwardbenson

To pull down tasks for a `@edwardbenson`, refreshing every day

	python monitor.py --tasks add ScrapeUser 1 86400 @edwardbenson

To sample from the stream for tweets that match the query `"Red Sox" Redsox` and print these out every 10 seconds

	python monitor.py --tasks add StartFilterStream "Red Sox" Redsox
    python monitor.py --tasks add DumpTweets 1 10
	
To sample from the stream, and every hour pull down the last 20 tweets from 10 random users

	python monitor.py --tasks add StartStream 
	python monitor.py --tasks add PullRandomUsers 1 3600 10 20

To shutdown the agent:
    python monitor.py --tasks add Die 


Tasks
-------------

### Basic Task Operations

**To add a task**:
	
	python monitor.py --tasks add <TaskName> <Repeat> <Delta>

For adding a task, `<Repeat>` is either 0 or 1, and `<Delta>` is the time
between repetitions. Set it to 0 if `<Repeat>` is also 0.

**To list tasks**:

	python monitor.py --tasks list

### ScrapeUser

Pulls tweets from the provided user, such as `@edwardbenson`

	python monitor.py --tasks add ScrapeUser <repeat> <delta> <username>

### StartStream

Starts pulling form the twitter stream
    
    python monitor.py --tasks add StartStream 0 0

### StopStream

Stops pulling form the twitter stream

    python monitor.py --tasks add StopStream 0 0

### StartFilterStream

Starts pulling form the filtered twitter stream with the provided args

    python monitor.py --tasks add StartFilterStream 0 0 <arg1> .. <argN>

### StopFilterStream

Stops pulling form the filtered twitter stream

    python monitor.py --tasks add StartFilterStream 0 0 

### PullRandomUsers

Queries for N random users in the database with only 1 tweet recorded in the DB 
and pulls their latest M tweets.

    python monitor.py --tasks add PullRandomUsers 0 0 <N> <M> 

Custom Tasks
-------------

Implementing your own tasks is easy. Just dig around in the `tasks/tasks.py` file to see examples.
