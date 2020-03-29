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

get_num = r'/gunnconfessions/posts/(\d+)'

page = PyQuery(facebook_base + '/pg/gunnconfessions/posts/')
epic_script_tag = page.find('script').filter(lambda i, this: PyQuery(this).text().startswith('new (require("ServerJS"))()'))
post_info = json.loads(epic_script_tag.text()[35:-2])
is_feedback = lambda json: isinstance(json, dict) and 'feedback' in json
feedback_things = []
searchJSON(feedback_things, is_feedback, post_info)
post_id_to_feedback = {}
for feedback_thing in feedback_things:
    id = feedback_thing['feedback']['share_fbid']
    post_id_to_feedback[id] = feedback_thing['feedback']
for confession in page.find('._3576').items():
    # print('#1: ' + confession.text())
    post_link = confession.parent().find('span > a._5pcq').attr('href')
    post_id = re.match(get_num, post_link).group(1)
    # page = PyQuery(facebook_base + post_link)
    # print(facebook_base + post_link)
    # print(post_id + ' ' + str(post_id in post_id_to_feedback))
    with open('./dumb-fb.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(post_id_to_feedback[post_id], indent=2))
    break

# see_more = page.find('#www_pages_reaction_see_more_unitwww_pages_posts a[ajaxify]').attr('ajaxify')
# # For some reason `__a=1` is necessary
# response = requests.get(facebook_base + see_more + '&__a=1')
# see_more = PyQuery(json.loads(response.content[9:])['domops'][0][3]['__html'])
# for confession in see_more.find('._3576').items():
#     # print('#2: ' + confession.text())
#     pass
