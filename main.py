import json
from bs4 import BeautifulSoup, SoupStrainer
import requests
import tweepy
import webbrowser

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'}

defaultKeywords=["cyber","security","hack","malware","python","programming",".net","windows","apple","hosting","breach","android","phone","software","computer","email","data","science"]

# Twitter Authentication
auth = tweepy.OAuthHandler("", # api key
    "") # api key secret
auth.set_access_token("", # access token
    "") # access token secret
api = tweepy.API(auth)

tags="#tech #programming #article #news"

# Send out the tweet
def tweet(title,url,description=""):
    api.update_status("\"{0}\"\n{1}\n{2}\n{3}".format(title,description,tags,url))

def keywordsInString(s):
    return any(kw in s.lower() for kw in defaultKeywords)

def scrapePageHN(i,newest=False):
    try:
        # we use requests to get the source of our the page
        if newest:
            requestUrl='https://news.ycombinator.com/newest?n='+str((30*(i-1))+1) # multiply the page number by 30 so page number is compatible with the new posts system
        else:
            requestUrl='https://news.ycombinator.com/news?p='+str(i)

        res=requests.get(requestUrl,headers = headers)

        if res.status_code != 200:
            print("error",res.status_code,requestUrl)

        only_td = SoupStrainer('td') # get all table data cells
        soup = BeautifulSoup(res.content, 'html.parser', parse_only=only_td) # parse the page source
        tdtitle = soup.find_all('td', attrs={'class':'title'}) # get all table data cells with class 'title'
        tdrank = soup.find_all('td', attrs={'class':'title', 'align':'right'}) # get all table data cells with class 'title' and alignment 'right'
        tdtitleonly = [t for t in tdtitle if t not in tdrank] # get all td's with class title that don't have alignment 'right'
        num_iter = min(len(tdrank), len(tdtitleonly)) # get number of articles on page (normally 29, can differ)

        for idx in range(num_iter):
            title = tdtitleonly[idx].find('a', attrs={'class':'storylink'}) # get the title text

            if not keywordsInString(title.text):
                continue # do not finish this iteration, continue straight on to the next

            url = title['href'] # get url

            print('Article Title:',title.text)
            print('URL:',url)
            print("-"*20) # visual separator

            if input("open? (y/n): ") == "y":
                webbrowser.open_new_tab(url)
            if input("tweet? (y/n): ") == "y":
                tweet(title.text,url,input("description: "))

            print()

    except (requests.ConnectionError, requests.packages.urllib3.exceptions.ConnectionError) as e:
        print('Connection Failed for page {}'.format(i))
    except requests.RequestException as e:
        print("Some ambiguous Request Exception occurred. The exception is "+str(e))

def hackerNews(new=False):
    for i in range(1, 20 + 1): # scrape the first 20 HN pages
        scrapePageHN(i,new)

def reddit(url):
    jsondat=json.loads(requests.get(url,headers = headers).text)["data"]["children"] # download and parse json string and select the appropriate child
    for post in jsondat: # iterate over post objects
        data=post["data"] # select post data
        if "url_overridden_by_dest" in data.keys(): # if post is a url (rather than text)
            title=data["title"] # get title from data

            if not keywordsInString(title):
                continue # do not finish this iteration, continue straight on to the next

            url=data["url"] # get url from data

            print('Article Title:',title)
            print('URL:',url)
            print("-"*20) # visual separator

            if input("open? (y/n): ") == "y":
                webbrowser.open_new_tab(url)
            if input("tweet? (y/n): ") == "y":
                tweet(title,url,input("description: "))
            print()

reddit("https://www.reddit.com/r/tech/new.json")
hackerNews()
