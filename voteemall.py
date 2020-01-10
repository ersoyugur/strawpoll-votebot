import requests, argparse, time
import threading

def parse_arguments():
    
    parser = argparse.ArgumentParser(
             description="strawpoll vote-bot. example: python3 voteemall.py 1111111 1",
             epilog="(c) 2020 Uger",
             fromfile_prefix_chars="@",
             add_help=False,
    )

    parser.add_argument("id", help="strawpoll.me poll ID")
    parser.add_argument("option", help="checkbox value")
  
    parser.add_argument("-t", help="max threads (Default: 10)")
    parser.add_argument("-p", action="store_true", help="Use proxies")
 
    return parser.parse_args()

"""
def startTorSession():
    session  = requests.session()
    session.proxies = {'http': 'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}

    return session
"""

def voteemAll(url, checkboxID, headers, proxy=None):
    if (proxy == None):
        proxies = {}
    else:
        proxies = {"https": proxy}

    try:
        page = requests.get(url, headers=headers, proxies=proxies, timeout=10).text
	secToken1 = page [page.find ("security-token"):]
	secToken1 = secToken1 [secToken1.find ("value=\"") + len ("value=\""):]
	secToken1 = secToken1 [:secToken1.find ("\"")]

	secToken2 = page [page.find ("field-authenticity-token"):]
	secToken2 = secToken2 [secToken2.find ("name=\"") + len ("name=\""):]
	secToken2 = secToken2 [:secToken2.find ("\"")]

	#page = startTorSession().post (url, data = {"security-token": secToken1, secToken2: "", "options": checkboxID}, headers = headers, timeout = 10).text
	page = requests.post (url, data = {"security-token": secToken1, secToken2: "", "options": checkboxID}, headers = headers, timeout = 10, proxies=proxies).text
        successString = "\"success\":\"success\""
	if (page.find (successString) != -1):
            print ("Vote Successful ({})".format (secToken1))
	else:
	    print ("Vote Unsuccessful ({})".format (secToken1))
    except requests.exceptions.ProxyError:
	print ("Vote Unsuccessful (Invalid Proxy)")
    except requests.exceptions.ConnectionError:
	print ("Vote Unsuccessful (Invalid Proxy - Connection Error)")

def prepVoting(args):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'}
    url = "https://www.strawpoll.me/" + args.id
    opt = str(args.option).strip()
    if args.p == True:
        try:
            proxies = open("proxies.txt","r").read().split("\n")
            print ("Found proxies.txt file, using that")
        except:
            print ("Getting proxies from an on-line source...")
	    page = requests.get ("https://proxy-daily.com", headers = headers).text
	    page = page [page.find ("centeredProxyList freeProxyStyle"):]
	    page = page [page.find (">") + 1:]
	    page = page [:page.find ("</div>")]
	    proxies = page.split ("\n")
	    print ("Loaded {} proxies.".format (len (proxies)))

    if args.t == None:
        maxthreads = 10
    else:
        maxthreads = int (args.t)

    print("Connecting to: " + url)
    page = requests.get (url, headers = headers).text
    ind = page.find("field-options-"+opt.replace(' ', '-')) 
    
    if (int == -1):
        print("Couldn't find the option " + opt)
        exit(1)

    checkboxID = page[ind:]
    checkboxID = checkboxID[checkboxID.find("value=\""):].splitlines()[0].split("value=\"")[1].strip("\"")
     
    print("Checkbox ID:" + checkboxID) 
    print("Max threads: " + str(maxthreads))

    proxyindex = 0
    while True:
        if args.p:
            proxy = proxies[proxyindex]
            proxyindex += 1
            if (proxyindex >= len (proxies)):
                print('All proxies have been used...')
                break
 
        else:
            proxy = None
              
        thr = threading.Thread (target = voteemAll, args = (url, checkboxID, headers, proxy))
        thr.daemon = True
        thr.start()
        
        while(threading.active_count () >= maxthreads):
            time.sleep(0.1)
 
def main():
    prepVoting(parse_arguments())

main() 
