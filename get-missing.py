import json

import scraper
import utils

max = 9632

def make_search(query):
    return 'https://www.facebook.com/ajax/pagelet/generic.php/PagePostsSearchResultsPagelet?data=%7B%22page_id%22%3A%221792991304081448%22%2C%22search_query%22%3A%22%s%22%7D&__a=1' % query

with open('./output/posts_2020-03-29_16.21.50.json', 'r', encoding='utf-8') as file:
    confessions = json.loads(file.read())

numbers = set([utils.get_confession_number(confession['content']) for confession in confessions])

for i in range(9000, max + 1):
    if i not in numbers:
        print('Missing confession #%d' % i)
