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

Tasks
-----

Implementing your own tasks is easy. Just dig around in the code to see how.


