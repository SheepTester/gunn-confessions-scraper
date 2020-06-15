import json
import urllib.parse
import requests
from pyquery import PyQuery
from datetime import datetime

import scraper
import post

def make_search(query):
    data = urllib.parse.quote(json.dumps({
        'page_id': '1792991304081448',
        'search_query': query
    }))
    path = '/ajax/pagelet/generic.php/PagePostsSearchResultsPagelet?data=%s&__a=1' % data
    return scraper.parse_facebook_json(requests.get(scraper.facebook_base + path).text)

def parse_search(query):
    search = make_search(query)
    page = PyQuery(search['payload'])
    post_id_to_feedback = scraper.parse_posts(search)
    return [scraper.make_post(post_id_to_feedback, confession) for confession in page.find('._307z').items()]

# conf = confession
def fetch_missing_posts(filename, maxConf=None, minConf=1):
    with open(filename, 'r', encoding='utf-8') as file:
        confessions = post.make_id_map([post.deserialize(item) for item in json.loads(file.read())])

    if maxConf == None:
        maxConf = max(confessions.keys())

    temp_file = open('./output/_posts_less_missing.json', 'w', encoding='utf-8')

    since_last = 0
    for i in range(maxConf, minConf - 1, -1):
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
    fetch_missing_posts('./output-dist/posts_2020-03-29_16.21.50.json', 9632, 9000)
