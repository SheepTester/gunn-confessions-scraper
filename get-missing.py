import json
import urllib.parse
import requests
from pyquery import PyQuery

import scraper
import utils

max = 9632

def make_search(query):
    data = urllib.parse.quote(json.dumps({
        'page_id': '1792991304081448',
        'search_query': query
    }))
    path = '/ajax/pagelet/generic.php/PagePostsSearchResultsPagelet?data=%s&__a=1' % data
    return scraper.parse_facebook_json(requests.get(scraper.facebook_base + path).text)

if __name__ == '__main__':
    search = make_search('survey')
    page = PyQuery(search['payload'])
    # file = open('./output/post.html', 'w', encoding='utf-8')
    # file.write(search['payload'])
    post_id_to_feedback = scraper.parse_posts(search)
    posts = [scraper.make_post(post_id_to_feedback, confession) for confession in page.find('._307z').items()]
    print('\n\n'.join([repr(post) for post in posts]))

# with open('./output/posts_2020-03-29_16.21.50.json', 'r', encoding='utf-8') as file:
#     confessions = json.loads(file.read())
#
# numbers = set([utils.get_confession_number(confession['content']) for confession in confessions])
#
# for i in range(9000, max + 1):
#     if i not in numbers:
#         print('Missing confession #%d' % i)
