from datetime import datetime
from pyquery import PyQuery
import urllib.parse
import requests
import json
import re
from post import Post

# Class key
# ._3576 - a <div>, the parent of each <p> in a post
# ._5pcq - the timestamp that links to the post page
# ._5-jo - The class for the <span> containing the confession text in search results
# ._lie  - The post link in search results

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
get_post_id_2 = r'feed_subtitle_1792991304081448;(\d+)' # For posts with photos
external_link = 'l.facebook.com'

def is_epic_script_tag(i, this):
    return PyQuery(this).text().startswith('new (require("ServerJS"))()')
def is_feedback(json):
    return isinstance(json, dict) and 'share_fbid' in json

def make_post(post_id_to_feedback, confessionWrapper):
    confession = confessionWrapper.find('._3576, ._5-jo')

    post_link = confessionWrapper.find('span > a._5pcq, ._lie')
    post_url = post_link.attr('href')
    post_id_search = re.search(get_post_id, post_url)
    if not post_id_search:
        post_link = post_link.closest('[id^="feed_subtitle_"]')
        post_id_search = re.search(get_post_id_2, post_link.attr('id'))
        if not post_id_search:
            print(post_url)
            with open('./output/photo_dumb.html', 'w', encoding='utf-8') as file:
                file.write(confessionWrapper.html())
            raise Exception('Could not find post ID in %s' % post_url)
    post_id = post_id_search.group(1)
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

def parse_facebook_json(fb_json):
    return json.loads(fb_json[9:])

def parse_posts(post_info):
    feedback_things = search_json([], is_feedback, post_info)
    post_id_to_feedback = {}
    for feedback_thing in feedback_things:
        id = feedback_thing['share_fbid']
        post_id_to_feedback[id] = feedback_thing
    return post_id_to_feedback

def fetch_post(post_id):
    page = PyQuery(facebook_base + '/gunnconfessions/posts/' + post_id, headers={'cookie': 'noscript=1'})
    epic_script_tag = page.find('script').filter(is_epic_script_tag)
    post_info = json.loads(epic_script_tag.text()[35:-2])

    post_id_to_feedback = parse_posts(post_info)
    return make_post(post_id_to_feedback, page.find('._3576').parent())

def fetch_posts(path, first):
    if first:
        page = PyQuery(facebook_base + path)
        epic_script_tag = page.find('script').filter(is_epic_script_tag)
        post_info = json.loads(epic_script_tag.text()[35:-2])
    else:
        response = parse_facebook_json(requests.get(facebook_base + path).text)
        page = PyQuery(response['domops'][0][3]['__html'])
        post_info = response['jsmods']

    post_id_to_feedback = parse_posts(post_info)
    posts = [make_post(post_id_to_feedback, confession.parent()) for confession in page.find('._3576').items()]

    see_more = page.find('#www_pages_reaction_see_more_unitwww_pages_posts a[ajaxify]').attr('ajaxify')
    return (posts, see_more + '&__a=1' if see_more is not None else None)

def fetch_all_pages():
    temp_file = open('./output/_posts.json', 'w', encoding='utf-8')

    pages = 1
    (posts, next) = fetch_posts('/pg/gunnconfessions/posts/', True)
    while next:
        (morePosts, next) = fetch_posts(next, False)
        posts += morePosts
        temp_file.write(json.dumps([post.serialize() for post in posts], indent=2))

        print('Page %d fetched' % pages)
        pages += 1

    temp_file.close()

    filename = './output/posts_%s.json' % datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(json.dumps([post.serialize() for post in posts], indent=2))
    return filename

if __name__ == '__main__':
    fetch_all_pages()
