from pyquery import PyQuery
import requests
import json

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

page = PyQuery(facebook_base + '/pg/gunnconfessions/posts/')
epic_script_tag = page.find('script').filter(lambda i, this: PyQuery(this).text().startswith('new (require("ServerJS"))()'))
# print('\n\n'.join([x.text()[0:30] for x in page.find('script').items()]))
post_info = json.loads(epic_script_tag.text()[35:-2])
is_feedback = lambda json: isinstance(json, dict) and 'feedback' in json
feedback_things = []
searchJSON(feedback_things, is_feedback, post_info)
for feedback_thing in feedback_things:
    print(feedback_thing['feedback']['share_fbid'])
for confession in page.find('._3576').items():
    # print('#1: ' + confession.text())
    post_link = confession.parent().find('span > a._5pcq').attr('href')
    # page = PyQuery(facebook_base + post_link)
    # print(facebook_base + post_link)
    # with open('./dumb-fb.html', 'w', encoding='utf-8') as f:
    #     f.write(page.html(method='html'))
    print(post_link)

# see_more = page.find('#www_pages_reaction_see_more_unitwww_pages_posts a[ajaxify]').attr('ajaxify')
# # For some reason `__a=1` is necessary
# response = requests.get(facebook_base + see_more + '&__a=1')
# see_more = PyQuery(json.loads(response.content[9:])['domops'][0][3]['__html'])
# for confession in see_more.find('._3576').items():
#     # print('#2: ' + confession.text())
#     pass
