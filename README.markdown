Twitter Scraper
===============

This is a light-weight agent-based framework to help you schedule a workflow of
scraping tasks.

Running
------- 

First, run the agent:
    
    python agent.py

This agent runs in the backround and does things based on the tasks that are 
assigned to it. You can schedule tasks using another commandline tool.

    python monitor.py tasks list
    python monitor.py task delete 1
    python monitor.py tasks add <TaskName> <Repeat> <Delta>

For adding a task, `<Repeat>` is either 0 or 1, and `<Delta>` is the time
between repititions. Set it to 0 if `<Repeat>` is also 0.

Bundled Tasks
-------------

A number of tasks come prepackaged with the library.

- **ScrapeUser** scrapes the history of a single user
- **ScrapeNyc** scrapes events from NYC.com
- **ScrapeTerms** subscripts to the feed for a set of terms

Operation of each of these is detailed below.

### ScrapeUser

To add:
    python monitor.py tasks add ScrapeUser <repeat> <delta> <username>

The username is the user's twitter handle, such as `@edwardbenson`

### ScrapeNyc

To add:
    
    python monitor.py tasks add ScrapeNyc <repeat> <delta>


### ScrapeTerms

The ScrapeTerms task is different than the others. This task stays 
running all the time and you can add and remove to the terms being 
scraped from the command line. Therefore it gets special handling.
(This is a useful utility first, a totally generalized one second)

    python monitor.py terms add <term1> <term2> .. <termN>
    python monitor.py terms remove <term1> <term2> .. <termN>
    python monitor.py terms list

Each of these terms will constitute a different search of the feed.
If you want the term to be multi-word, use a space.

Custom Tasks
-------------

Implementing your own tasks is easy. Just dig around in the code to see how.


