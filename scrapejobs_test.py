import asyncio, concurrent.futures, random, re, requests, sys
from bs4 import BeautifulSoup



ports = [str(port) for port in range(12000, 13001)]
base_url = ("https://www.linkedin.com/jobs/search/?pageNum=0&position=1&location=lebanon")
subdict = {}
retries = 0
while retries<6:
    try:
        PORT = random.choice(ports)
        res = requests.get(base_url, proxies={'https':'199.189.86.111:'+PORT}, timeout=60)
        res.raise_for_status()
        if res.status_code == 999:
            raise Exception
        soup = BeautifulSoup(res.text, "html.parser")
        # for platform in social:
        #     link = soup.find('a', href=social[platform])
        #     if link:
        #         subdict[platform] = link['href']
        #     else:
        #         subdict[platform] = None
        # playlists.update_one({'_id':playlist['_id']}, {'$set':{'SocialMedia':subdict}})
        #print(playlist['_id'])
        #print(subdict)
        break
    except KeyboardInterrupt:
        sys.exit()
    except Exception:
        retries += 1