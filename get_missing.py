import json
import urllib.parse
import requests
from pyquery import PyQuery
from datetime import datetime
import time

import scraper
import post

def make_search(query):
    data = urllib.parse.quote(json.dumps({
        'page_id': '1792991304081448',
        'search_query': query
    }))
    path = '/ajax/pagelet/generic.php/PagePostsSearchResultsPagelet?data=%s&__a=1' % data
    try:
        parsed_json = scraper.parse_facebook_json(requests.get(scraper.facebook_base + path).text)
    except:
        print('There was a problem getting %s. Retrying in five seconds.' % query)
        time.sleep(5)
        parsed_json = scraper.parse_facebook_json(requests.get(scraper.facebook_base + path).text)
    return parsed_json

def parse_search(query):
    search = make_search(query)
    page = PyQuery(search['payload'])
    post_id_to_feedback = scraper.parse_posts(search)
    return [scraper.make_post(post_id_to_feedback, confession) for confession in page.find('._307z').items()]

# conf = confession
def fetch_missing_posts(filename, max_conf=None, min_conf=1):
    with open(filename, 'r', encoding='utf-8') as file:
        confessions = post.make_id_map([post.deserialize(item) for item in json.loads(file.read())])

    # Delete confession with key None (1st arg) and if it doesn't exist, return None (2nd arg)
    confessions.pop(None, None)

    if max_conf == None:
        max_conf = max(confessions.keys())

    temp_file = open('./output/_posts_less_missing.json', 'w', encoding='utf-8')

    since_last = 0
    for i in range(max_conf, min_conf - 1, -1):
        if i not in confessions:
            found = post.make_id_map(parse_search(str(i)))
            confessions.update(found)
            print('Was missing confession #%d; found %s' % (i, ' '.join(map(str, found.keys())) or '[presumably deleted]'))

            # Save every 20 iterations
            since_last += 1
            if since_last > 20:
                temp_file.write(json.dumps([conf.serialize() for conf in confessions.values()], indent=2))
                since_last = 0
                print('Saved')

    temp_file.close()

    filename = './output/posts_%s_less_missing.json' % datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(json.dumps([conf.serialize() for conf in confessions.values()], indent=2))
    return filename

if __name__ == '__main__':
    # fetch_missing_posts('./output-dist/posts_2020-03-29_16.21.50.json', 9632, 9000)
    fetch_missing_posts('./output/last_backup_2020-06-15_18.08.37.json', 8536)
