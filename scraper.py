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

get_num = r'/gunnconfessions/posts/(\d+)'

class Post:
    def __init__(self, content, timestamp, comments, reactions):
        self.content = content
        self.timestamp = timestamp
        self.comments = comments
        self.reactions = reactions

    def __repr__(self):
        return 'Post(%s, %s, %s, %s)' % (self.content, self.timestamp, self.comments, self.reactions)

def is_epic_script_tag(i, this):
    return PyQuery(this).text().startswith('new (require("ServerJS"))()')
def is_feedback(json):
    return isinstance(json, dict) and 'share_fbid' in json

posts = []

page = PyQuery(facebook_base + '/pg/gunnconfessions/posts/')

# Get feedback things from the epic script tag...
epic_script_tag = page.find('script').filter(is_epic_script_tag)
post_info = json.loads(epic_script_tag.text()[35:-2])
feedback_things = searchJSON([], is_feedback, post_info)
post_id_to_feedback = {}
for feedback_thing in feedback_things:
    id = feedback_thing['share_fbid']
    post_id_to_feedback[id] = feedback_thing

def make_post(confessionElem):
    text = confessionElem.text()

    post_link = confessionElem.parent().find('span > a._5pcq')
    post_id = re.match(get_num, post_link.attr('href')).group(1)
    feedback = post_id_to_feedback[post_id]

    timestamp = int(post_link.find('[data-utime]').attr('data-utime'))
    comments = feedback['comment_count']['total_count']

    reactions = {}
    if 'top_reactions' in feedback:
        for reaction in feedback['top_reactions']['edges']:
            reactions[reaction['node']['reaction_type']] = reaction['reaction_count']

    return Post(text, timestamp, comments, reactions)

posts += map(make_post, page.find('._3576').items())

print(posts)

# see_more = page.find('#www_pages_reaction_see_more_unitwww_pages_posts a[ajaxify]').attr('ajaxify')
# # For some reason `__a=1` is necessary
# response = requests.get(facebook_base + see_more + '&__a=1')
# see_more = PyQuery(json.loads(response.content[9:])['domops'][0][3]['__html'])
# for confession in see_more.find('._3576').items():
#     # print('#2: ' + confession.text())
#     pass
