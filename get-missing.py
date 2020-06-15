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

if __name__ == '__main__':
    with open('./output-dist/posts_2020-03-29_16.21.50.json', 'r', encoding='utf-8') as file:
        confessions = post.make_id_map([post.deserialize(item) for item in json.loads(file.read())])

    max = 6752

    for i in range(6750, max + 1):
        if i not in confessions:
            found = post.make_id_map(parse_search(str(i)))
            confessions.update(found)
            print('Was missing confession #%d; found %s' % (i, ' '.join(map(str, found.keys()))))

    with open('./output/posts_%s_less_missing.json' % datetime.now().strftime('%Y-%m-%d_%H.%M.%S'), 'w', encoding='utf-8') as file:
        file.write(json.dumps([conf.serialize() for conf in confessions.values()], indent=2))
