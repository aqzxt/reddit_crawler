import requests, os
from bs4 import BeautifulSoup as soup
from flask import (Flask, session, render_template, request, flash, jsonify)

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


def crawl_reddit(thread_input, upvotes_target, max_subreddits, max_trending_pages, starting_url):
    '''params
        thread_input        ->  User input threads separated by ";"
        upvotes_target      ->  Determine the minimum upvotes
        max_subreddits      ->  Maximum number of subreddits to search
        max_trending_pages  ->  Number of trending pages to process. Default: 1.
        starting_url        ->  User custom starting trending subreddits URL. Default: None
        
        Reddit Crawler script. Search subreddits (limitted to 5, by reddit website) with minimum of 5k upvotes, based on the (latest URL, by default) trending subreddits available.
        
        Output:
        If any, prints data to STDOUT, line by line, followed by an empty one every new subreddit
        If none, prints a message
    '''

    # Add real user agent
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'

    # Max number of subreddits per page is 125 (25 trending subreddits x 5 subreddits). 
    max_subr_pages = 1
    
    # Loop for how many trending subreddits pages the user input. Default: 1
    for page in range(max_subr_pages):
        
        # === If user submitted custom threads
        # === Proceed to process the trending page
        if not thread_input:
            
            # ===== STARTING TRENDING SUBREDDITS PAGE ========
            
            # === Collect all subreddit urls ===
            # If first iteration
            if page == 0:

                # Use default if none
                if starting_url == None:
                    starting_url = 'https://old.reddit.com/r/trendingsubreddits/'
                    
                if type(starting_url) != str:
                    return "ERROR: Expected 'starting_url' of type <class 'str'>. Got " + str(type(starting_url))
                
                pattern = 'old.reddit.com/r/trendingsubreddits'
                
                if pattern not in starting_url:
                    return "ERROR: Input 'starting_url' is not a valid URL."
                
                if not starting_url.startswith('http'):
                    starting_url = 'https://' + starting_url
                    
                response = requests.get(starting_url, headers = {'User-agent': user_agent})
                
            else:
                # Subsequent pages
                url = trendings_page.find('span', {'class':'next-button'}).a.get('href')
                
                # Halt looping if there are no more next pages
                if not url: break
                    
                response = requests.get(url, headers = {'User-agent': user_agent})

            if not response.ok:
                return 'ERROR Response code: ' + str(response.status_code)
                
            # Parse and store html response
            trendings_page = soup(response.text, 'lxml')


            # ============ LIMIT NUMBER OF SUBREDDITS TO SEARCH (default: 25) ============
            
            # If last iteration
            if page == max_subr_pages -1:
                a_tags = trendings_page.find_all('a', {'class': 'bylink'}, limit=max_subreddits)
            
            # Otherwise number of trending is still higher than 125 (the max value per page)
            else:
                a_tags = trendings_page.find_all('a', {'class': 'bylink'})

            # Store only valid urls
            # i.e. 'https://old.reddit.com/r/trendingsubreddits/comments/a13eio/trending_subreddits_for_20181128_rstarwars/'
            valid_subr_urls = []
            for tag in a_tags:
                valid_subr_urls.append(tag.attrs.get('href'))
            
            
            # ======== CHILD PAGE WITH 5 SUBREDDITS LINKS EACH =========
            
            # Collect all the individual subreddit html pages
            trending_list = []
            for i in range(len(valid_subr_urls)):
                
                subr = valid_subr_urls[i]

                response = requests.get(subr, headers = {'User-agent': user_agent})
                if not response.ok:

                    return "ERROR: There was a server error. Code: " + str(response.status_code)

                
                trending_list.append(soup(response.text, 'lxml'))
                
                
            # ======= LIMIT NUMBER OF TRENDING SUBREDDITS TO PROCESS (default: 1 -> Skips first loop) =========
            
            # Extract all <strong> tags from each page, each containing <a> subreddit url
            strong_tag_list = []
            for i in range(len(trending_list)):
                strong_tag_list.append(trending_list[i].find_all('strong'))
                
            # Extract all <a> from each <strong>
            url = 'https://old.reddit.com'
            subreddits = []
            for strong_tag in strong_tag_list:
                
                # strong_tag (list): most of length 6. Max of 11
                for a_tag in strong_tag:
                    if a_tag.a:
                        # Build full subreddit url > "https://old.reddit.com" + "/r/nasa"
                        subreddits.append(url + a_tag.a.text)


        if thread_input:
            thread_input = thread_input.split(';')
            # Build list urls
            url = 'https://old.reddit.com/r/'
            subreddits = []
            for subr in thread_input:
                subreddits.append(url + subr)
        
        # ======= INDIVIDUAL SUBREDDIT PAGE ==========
        
        # Get upvotes, subreddit, subreddit title, comments link and thread link
        
        subr_page = []
        for subr in subreddits:

            response = requests.get(subr, headers = {'User-agent': user_agent})
            if not response.ok:
                return "ERROR: There was a server error. Code: " + str(response.status_code)
            
            subr_page.append(soup(response.text, 'lxml'))
            
            # Deal with extra pages
            for page in range(max_trending_pages-1):
                
                next_url = subr_page[-1].find('span', {'class': 'next-button'}).a.get('href')
                response = requests.get(next_url, headers = {'User-agent': user_agent})
                
                if not response.ok:
                    return "ERROR: There was a server error. Code: " + str(response.status_code)
                
                subr_page.append(soup(response.text, 'lxml'))
            
        
        # Get all html 'div' tags with a 'top-matter' class
        upvotes = []
        top_matter = []
        for subr in subr_page:
            
            upvotes.append(subr.find_all('div', {'class': 'likes'}))
            top_matter.append(subr.find_all('div', {'class': 'top-matter'}))
        
        # Containers to store the goods
        stats = [[] for i in range(5)]
        for k in range(len(upvotes)):
            for i in range(len(upvotes[k])):
                
                # Filter by upvotes
                curr = upvotes[k][i].attrs.get('title')
                
                # Make sure curr is not None and it's above target
                if curr and int(curr) >= upvotes_target: 
                    stats[0].append(curr)
                    
                    comments_url = top_matter[k][i].find('a', {'class':"bylink comments may-blank"})

                    if comments_url: comments_url = comments_url.attrs.get('href')
                    else: comments_url = ""
                    
                    c = comments_url.find('/comments/')
                    thread_url = comments_url[:c]
                    
                    subr_title = top_matter[k][i].p.text
                    if subr_title.startswith('image/gif'): a = 9
                    else: a = 0
                    b = subr_title.rfind(' (')
                    
                    subreddit_name = thread_url[25:]
                    
                    # Get all the remaining info
                    stats[1].append(subreddit_name)
                    stats[2].append(subr_title[a:b])
                    stats[3].append(comments_url)
                    stats[4].append(thread_url[:c])
        
        if len(stats[0]) == 0:
            return "Sorry. Based on your input, there are no trending subreddits with "+ str(upvotes_target) +" upvotes or higher. Try increasing how much subreddits to search (default: 3)."
        
        # Gathered information in a list for each Subreddit
        result = []
        for k in range(len(stats[0])):
            result.append([stats[0][k], stats[1][k], stats[2][k], stats[3][k], stats[4][k]])

        return result




@app.route("/", methods=["GET", "POST"])
def main():

    query = request.form.get("query")
    max_subr = request.form.get("max_subr")
    upvotes_target = request.form.get("upvotes_target")

    if not upvotes_target: upvotes_target = 5000
    if not max_subr: max_subr = 3

    # To submit user input
    if request.method == "POST":

        reddit = crawl_reddit(query, upvotes_target, max_subr, 1, None)

        # If error
        if type(reddit) == str:
            return render_template('results.html', reddit=reddit, msg=query)

        # Render results
        return render_template('results.html', reddit=reddit, query=query, msg=None)

    # If method == "GET"
    return render_template("main.html")


