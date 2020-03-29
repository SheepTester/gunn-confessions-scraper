from datetime import datetime
from pyquery import PyQuery
import requests
import json
import re

# Class key
# ._3576 - a <div>, the parent of each <p> in a post
# ._5pcq - the timestamp that links to the post page

facebook_base = 'https://www.facebook.com'

def searchJSON(matches, match_fn, json):
    if match_fn(json):
        matches.append(json)
    elif isinstance(json, list):
        for item in json:
            searchJSON(matches, match_fn, item)
    elif isinstance(json, dict):
        for val in json.values():
            searchJSON(matches, match_fn, val)
    return matches

get_post_id = r'/posts/(\d+)'

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

def make_post(post_id_to_feedback, confessionElem):
    text = confessionElem.text()

    post_link = confessionElem.parent().find('span > a._5pcq')
    post_id = re.search(get_post_id, post_link.attr('href')).group(1)
    feedback = post_id_to_feedback[post_id]

    timestamp = int(post_link.find('[data-utime]').attr('data-utime'))
    comments = feedback['comment_count']['total_count']

    reactions = {}
    if 'top_reactions' in feedback:
        for reaction in feedback['top_reactions']['edges']:
            reactions[reaction['node']['reaction_type']] = reaction['reaction_count']

    return Post(post_id, text, timestamp, comments, reactions)

def fetch_posts(path, first):
    if first:
        page = PyQuery(facebook_base + path)
        epic_script_tag = page.find('script').filter(is_epic_script_tag)
        post_info = json.loads(epic_script_tag.text()[35:-2])
    else:
        response = json.loads(requests.get(facebook_base + path).content[9:])
        page = PyQuery(response['domops'][0][3]['__html'])
        post_info = response['jsmods']

    feedback_things = searchJSON([], is_feedback, post_info)
    post_id_to_feedback = {}
    for feedback_thing in feedback_things:
        id = feedback_thing['share_fbid']
        post_id_to_feedback[id] = feedback_thing

    posts = [make_post(post_id_to_feedback, confession) for confession in page.find('._3576').items()]

    see_more = page.find('#www_pages_reaction_see_more_unitwww_pages_posts a[ajaxify]').attr('ajaxify')
    return (posts, see_more + '&__a=1' if see_more is not None else None)

temp_file = open('./output/_posts.json', 'w', encoding='utf-8')

(posts, next) = fetch_posts('/pg/Test-Confessions-Page/posts/', True)
while next:
    (morePosts, next) = fetch_posts(next, False)
    posts += morePosts
    temp_file.write(json.dumps([post.__dict__ for post in posts]))

temp_file.close()

with open('./output/posts_%s.json' % datetime.now().strftime('%Y-%m-%d_%H.%M.%S'), 'w', encoding='utf-8') as file:
    file.write(json.dumps([post.__dict__ for post in posts], indent=2))
