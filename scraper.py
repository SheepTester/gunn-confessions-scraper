from datetime import datetime
from pyquery import PyQuery
import urllib.parse
import requests
import json
import re

# Class key
# ._3576 - a <div>, the parent of each <p> in a post
# ._5pcq - the timestamp that links to the post page

facebook_base = 'https://www.facebook.com'

def search_json(matches, match_fn, json):
    if match_fn(json):
        matches.append(json)
    elif isinstance(json, list):
        for item in json:
            search_json(matches, match_fn, item)
    elif isinstance(json, dict):
        for val in json.values():
            search_json(matches, match_fn, val)
    return matches

get_post_id = r'/posts/(\d+)'
confession_number_regex = r'^(\d+)\. '
external_link = 'l.facebook.com'

def get_confession_number(confession_text):
    confession_number_match = re.search(confession_number_regex, confession_text)
    if confession_number_match:
        return int(confession_number_match.group(1))
    else:
        return 0

class Post:
    def __init__(self, post_id, content, timestamp, comments, reactions):
        self.content = content
        self.post_id = post_id
        self.timestamp = timestamp
        self.comments = comments
        self.reactions = reactions

    def __repr__(self):
        return 'Post(%s, %s, %s, %s, %s)' % (self.post_id, self.content, self.timestamp, self.comments, self.reactions)

def is_epic_script_tag(i, this):
    return PyQuery(this).text().startswith('new (require("ServerJS"))()')
def is_feedback(json):
    return isinstance(json, dict) and 'share_fbid' in json

def make_post(post_id_to_feedback, confession):
    post_link = confession.parent().find('span > a._5pcq')
    post_url = post_link.attr('href')
    post_id = re.search(get_post_id, post_url).group(1)
    feedback = post_id_to_feedback[post_id]

    timestamp = int(post_link.find('[data-utime]').attr('data-utime'))
    comments = feedback['comment_count']['total_count']

    reactions = {}
    if 'top_reactions' in feedback:
        for reaction in feedback['top_reactions']['edges']:
            reactions[reaction['node']['reaction_type']] = reaction['reaction_count']

    expandPost = confession.find('.text_exposed_link')
    if expandPost.length > 0:
        if expandPost.find('.see_more_link_inner').text().lower() == 'see more':
            # If it's "See more," then the post is actually already loaded, but
            # visually hidden.
            confession.find('.text_exposed_hide').remove()
        else:
            confession = PyQuery(facebook_base + post_url, headers={'cookie': 'noscript=1'}).find('._3576')

    for link in confession.find('a[target=_blank]').items():
        parsed_url = urllib.parse.urlparse(link.attr('href'))
        extlink_query = urllib.parse.parse_qs(parsed_url.query).get('u')
        if parsed_url.netloc == external_link and extlink_query and '…' in link.text():
            link.text(extlink_query[0])

    text = confession.text()

    return Post(post_id, text, timestamp, comments, reactions)

def fetch_posts(path, first):
    if first:
        page = PyQuery(facebook_base + path)
        epic_script_tag = page.find('script').filter(is_epic_script_tag)
        post_info = json.loads(epic_script_tag.text()[35:-2])
    else:
        response = json.loads(requests.get(facebook_base + path).text[9:])
        page = PyQuery(response['domops'][0][3]['__html'])
        post_info = response['jsmods']

    feedback_things = search_json([], is_feedback, post_info)
    post_id_to_feedback = {}
    for feedback_thing in feedback_things:
        id = feedback_thing['share_fbid']
        post_id_to_feedback[id] = feedback_thing

    posts = [make_post(post_id_to_feedback, confession) for confession in page.find('._3576').items()]

    see_more = page.find('#www_pages_reaction_see_more_unitwww_pages_posts a[ajaxify]').attr('ajaxify')
    return (posts, see_more + '&__a=1' if see_more is not None else None)

temp_file = open('./output/_posts.json', 'w', encoding='utf-8')

pages = 1
(posts, next) = fetch_posts('/pg/gunnconfessions/posts/', True)
while next:
    (morePosts, next) = fetch_posts(next, False)
    posts += morePosts
    temp_file.write(json.dumps([post.__dict__ for post in posts], indent=2))

    print('Page %d fetched' % pages)
    pages += 1

temp_file.close()

with open('./output/posts_%s.json' % datetime.now().strftime('%Y-%m-%d_%H.%M.%S'), 'w', encoding='utf-8') as file:
    file.write(json.dumps([post.__dict__ for post in posts], indent=2))
