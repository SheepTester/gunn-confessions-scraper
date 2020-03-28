from pyquery import PyQuery
import requests
import json

facebook_base = 'https://www.facebook.com'

page = PyQuery(facebook_base + '/pg/gunnconfessions/posts/')
for confession in page.find('._3576').items():
    # print('#1: ' + confession.text())
    pass

see_more = page.find('#www_pages_reaction_see_more_unitwww_pages_posts a[ajaxify]').attr('ajaxify')
# For some reason `__a=1` is necessary
response = requests.get(facebook_base + see_more + '&__a=1')
see_more = PyQuery(json.loads(response.content[9:])['domops'][0][3]['__html'])
for confession in see_more.find('._3576').items():
    print('#2: ' + confession.text())
