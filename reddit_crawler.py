import requests, click
from bs4 import BeautifulSoup as soup

@click.command()
@click.option('-i', '--subr_input', default=None)
@click.option('-s', '--max_subreddits', default=3)
@click.option('-t', '--max_trending_pages', default=1)
@click.option('-u', '--starting_url', default=None)
def crawl_reddit(subr_input, max_subreddits, max_trending_pages, starting_url):
    '''params
        subr_input     ->  User input subreddits separated by ";". Default: empty.
        max_subreddits ->  Maximum number of subreddits to process. Default: 3.
        max_trending_pages-> Number of trending pages to process. Default: 1.
        starting_url   ->  User custom starting trending subreddits URL. Default: None
        
        Reddit Crawler script. Search subreddits (limitted to 5, by default) with minimum of 5k upvotes, based on the (latest URL, by default) trending subreddits available.
        
        Output:
        If any, prints data to STDOUT, line by line, followed by an empty one every new subreddit
        If none, prints a message
    '''
    
    # Add real user agent
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'
    
    # If user inputted a list of subreddits i.e. "computerscience;space;nasa", validate it
    if subr_input:
        
        if type(subr_input) != str:
            raise TypeError("Expected 'subr_input' of type <class 'str'>. Got " + str(type(subr_input)))
        
        max_subr_pages = 1
    else:
        # Validate 'max_subreddits' and 'max_trending_pages'
        if type(max_subreddits) != int:
            raise TypeError("Expected 'max_subreddits' of type <class 'int'>. Got " + str(type(max_subreddits)))
            
        if type(max_trending_pages) != int and subr_input == None:
            raise TypeError("Expected 'max_trending_pages' of type <class 'int'>. Got " + str(type(max_trending_pages)))
        
        # By default, it's just a portion of the first page (0 < 5/125 < 1)
        # Max number of subreddits per page is 125 (5 per URL)
        max_subr_pages = (max_subreddits // 125) + 1

    # Loop for how many trending subreddits pages user inputted. Default: 1
    for page in range(max_subr_pages):
        
        # === If user submitted custom subreddits
        # === Proceed to process the trending page
        if subr_input == None:
            
            # ===== STARTING TRENDING SUBREDDITS PAGE ========
            
            # ==Collect all subreddit urls
            # If first iteration
            if page == 0:
                
                # Use default if none
                if starting_url == None:
                    starting_url = 'https://old.reddit.com/r/trendingsubreddits/'
                    
                if type(starting_url) != str:
                    raise TypeError("Expected 'starting_url' of type <class 'str'>. Got " + type(subr_input))
                
                pattern = 'old.reddit.com/r/trendingsubreddits'
                
                if pattern not in starting_url:
                    raise Exception("Input 'starting_url' is not a valid URL.")
                
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
                raise Exception('An error has occurred. Response code: ' + response.status_code)
                
            # Parse and store html response
            trendings_page = soup(response.text, 'lxml')
            

            # ============ LIMIT NUMBER OF SUBREDDITS TO SEARCH (default: 3) ============
            
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
                    raise Exception("There was a server error. Code: " + response.status_code)
                
                trending_list.append(soup(response.text, 'lxml'))
                
            print('Hold your horses!!\nWorking...\n')

                
            # ======= LIMIT NUMBER OF TRENDING SUBREDDITS TO PROCESS (default: 1 -> Skips loop) =========
            
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
        
        if subr_input != None:
            subr_input = subr_input.split(';')
            # Build list urls
            url = 'https://old.reddit.com/r/'
            subreddits = []
            for subr in subr_input:
                subreddits.append(url + subr)
        
        # ======= INDIVIDUAL SUBREDDIT PAGE ==========
        
        # Get upvotes, subreddit, subreddit title, comments link and thread link
        
        subr_page = []
        for subr in subreddits:

            response = requests.get(subr, headers = {'User-agent': user_agent})
            if not response.ok:
                raise Exception("There was a server error. Code: " + response.status_code)
            
            subr_page.append(soup(response.text, 'lxml'))
            
            # Deal with extra pages
            for page in range(max_trending_pages-1):
                
                next_url = subr_page[-1].find('span', {'class': 'next-button'}).a.get('href')
                response = requests.get(next_url, headers = {'User-agent': user_agent})
                
                if not response.ok:
                    raise Exception("There was a server error. Code: " + response.status_code)
                
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
                
                # Make sure curr is not None and it's above 5k
                if curr and int(curr) >= 5000: 
                    stats[0].append(curr)
                    
                    comments_url = top_matter[k][i].find('a', {'class':"bylink comments may-blank"}).attrs.get('href')
                    
                    c = comments_url.find('/comments/')
                    thread_url = comments_url[:c]
                    
                    subr_title = top_matter[k][i].p.text
                    t = subr_title.rfind(' (')
                    
                    subreddit_name = thread_url[25:]
                    
                    # Get all the remaining info
                    stats[1].append(subreddit_name)
                    stats[2].append(subr_title[:t])
                    stats[3].append(comments_url)
                    stats[4].append(thread_url[:c])
        
        if len(stats[0]) == 0:
            print("Sorry. Based on your input there are no trending subreddits with 5k upvotes or higher. Try increasing how much pages to process (default: 3).")
            return
        
        # Output gathered information
        for k in range(len(stats[0])):
            print('Upvotes: ' + stats[0][k])
            print('Subreddit: ' + stats[1][k])
            print('Thread Title: ' + stats[2][k])
            print('Comments URL: ' + stats[3][k])
            print('Thread URL: ' + stats[4][k] + '\n')
        return    


if __name__ == '__main__':
    crawl_reddit()