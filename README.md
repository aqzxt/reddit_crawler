# Reddit Crawler  

Based on this [challenge](https://github.com/idwall/desafios/tree/master/crawlers)

## Requirements  

Python 3  

- Dependencies:  

`requests`  [Requests docs](http://docs.python-requests.org/en/master/)  
`bs4`  [BeautifulSoup v4 docs](http://www.crummy.com/software/BeautifulSoup/bs4/doc/)  
`click`  [Click docs](https://click.palletsprojects.com/en/7.x/#documentation)  

- Installation:

```bash
$ pip install -r requirements.txt
```

### Main Application  

`reddit_crawler.py` file contains a function named `crawl_reddit()`

Can be run with no user inputs.  
Takes 4 optional parameters:  

- `-i`, `--subr_input`, default value: `None`, type: `str`:  
    User input subreddits separated by a semicolon (`;`)  
    Example: `"computerscience;nasa;space"`  
  
- `-s`, `--max_subreddits`, default value: `3`, type: `int`:  
    Maximum number of subreddits to process  
    Example: [/r/computerscience](https://www.reddit.com/r/computerscience), [/r/nasa](https://www.reddit.com/r/nasa), [/r/space](https://www.reddit.com/r/space/)  
  
- `-t`, `--max_trending_pages`, default value: `1`, type: `int`:  
    Number of trending pages to process. 25 URLs with 5 subreddits each, for a total of 125 subr per page.  
    Example of a trending page: [Trending Subreddits for 2018-11-27: /r/space, /r/nasa, /r/maybemaybemaybe, /r/thewalkingdead, /r/AbsoluteUnits](https://old.reddit.com/r/trendingsubreddits/comments/a0s13h/trending_subreddits_for_20181127_rspace_rnasa/)  

- `-u`, `--starting_url`, default: `None`, type: `str`:  
    User custom starting trending subreddits URL.  
    Value used: `https://old.reddit.com/r/trendingsubreddits`  

### Common usage scenarios

- **No user input. Only default values.**  

`$ python reddit_crawler.py`  


    1. Scan only 1 [Trending Subreddits](https://old.reddit.com/r/trendingsubreddits) page;  
    2. Process the first 3 subreddits URLs;  
    3. Check if each subreddit has a minimum of 5k upvotes;  
    4. Finally, store the data and print them, if any. Else, print a message.  

- **With user input**

`$ python reddit_crawler.py -i "space;nasa"`  
Or  
`$ python reddit_crawler.py --subr_input "space;nasa"`  


    1. Directly validate and process `subr_input` data, including converting it to subreddits URLs;  
    2. Do the steps 3 and 4 listed above.

### Goal

Generate and print a list of data scrapped from Trending Subreddits with at least 5000 upvotes to the screen (STDOUT) containing:  
  
- Upvotes number (minimum of 5k!);  
- Subreddit name;  
- Subreddit title;  
- Comments URL;  
- Thread URL.  

Sample output for 1 successfull request:

```bash
Upvotes: 12981
Subreddit: space
Thread Title: Planet Earth working on 3 Mars landers to follow InSight
Comments URL: https://old.reddit.com/r/space/comments/a2406d/planet_earth_working_on_3_mars_landers_to_follow/
Thread URL: https://old.reddit.com/r/space
```

Output for failed search:

```bash
Sorry. Based on your input there are no trending subreddits with 5k upvotes or higher. Try increasing how much pages to process (default: 3). Keep in mind it may take longer to process.
```

Script uses old Reddit layout based on the domain format [https://old.reddit.com/](https://old.reddit.com/) to process data.  

### TO DO

Build a Telegram Bot that interacts with `reddit_crawler.py` script and receives a response containing the list, upon the following command `/NothingToDo [+ Subrredit list]` (i.e. `/NothingToDo computerscience;nasa;space`).
