import os;
from urllib.parse import urlencode, quote;
import json;
import requests;

class Reaction:
    def __init__(self, raw_reaction):
        self.count = raw_reaction['reaction_count'];
        self.type = raw_reaction['node']['reaction_type'];

    def __repr__(self):
        return f'{self.type} x{self.count}'

class Comment:
    def __init__(self, raw_comment):
        raw_comment = raw_comment['node'];
        self.author = raw_comment['author']['name'];
        self.author_url = raw_comment['author']['url'];
        self.content = raw_comment['body']['text'] if raw_comment['body'] is not None else '';
        # *Seconds* since epoch
        self.created = raw_comment['created_time'];
        # There's also `edit_history`

    def __repr__(self):
        return f'{repr(self.content)} - {self.author}'

class Post:
    def __init__(self, raw_post):
        sections = raw_post['node']['comet_sections'];
        feedback = sections['feedback']['story']['feedback_context']['feedback_target_with_context'];

        self.post = sections['content']['story']['comet_sections']['message']['story']['message']['text'];
        self.comment_count = feedback['comment_count']['total_count'];
        self.reaction_count = feedback['comet_ufi_summary_and_actions_renderer']['feedback']['reaction_count']['count'];
        self.share_count = feedback['comet_ufi_summary_and_actions_renderer']['feedback']['share_count']['count'];
        self.reactions = [
            Reaction(reaction)
            for reaction in feedback['comet_ufi_summary_and_actions_renderer']['feedback']['top_reactions']['edges']
        ];
        self.comments = [
            Comment(comment)
            for comment in feedback['display_comments']['edges']
        ];
        self.created = sections['context_layout']['story']['comet_sections']['timestamp']['story']['creation_time'];
        self.url = sections['context_layout']['story']['comet_sections']['timestamp']['story']['url'];

    def __repr__(self):
        return f'{repr(self.post)} comments={self.comment_count} reactions={self.reaction_count} ({" ".join(map(repr, self.reactions))}) shares={self.share_count}' \
            + ''.join('\n' + repr(comment) for comment in self.comments);

class PageGetter:
    def __init__(self, page_id, doc_id):
        self.cookie = f'c_user={os.getenv("COOKIE_C_USER")}; xs={quote(os.getenv("COOKIE_XS"))}';
        self.page_id = page_id;
        self.doc_id = doc_id;

    def get_page(self, cursor=None, count=3):
        '''
        Fetches posts from the Facebook page with cookies as listed in `.env`.

        :param cursor: A string containing the next cursor to get the next set
        of posts, or `None` to get the first page.
        :param count: The number of posts to get. The maximum is 297, for some
        reason.
        :returns: A tuple with a list of `Post`s and the cursor for the next
        page.
        ''';

        body = urlencode({
            # No idea what this means, but it's needed
            'fb_dtsg': 'AQHS7sAiDqyR:AQHryv1x5_m1',

            # GraphQL document ID, apparently
            'doc_id': self.doc_id,

            'variables': json.dumps({
                'count': count,
                'cursor': cursor,

                # Needed for comments to be listed
                'feedLocation': 'PAGE_TIMELINE',

                # If omitted, Facebook gives a warning about it being omitted
                'privacySelectorRenderLocation': 'COMET_STREAM',

                # Gunn Confessions page ID
                'id': self.page_id,
            }),
        });
        response = requests.post(
            'https://www.facebook.com/api/graphql/',
            data=body,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': self.cookie,
            },
        ).json();
        posts = [
            Post(post)
            for post in response['data']['node']['timeline_feed_units']['edges']
            # The earliest post (or a pfp change) may have message: null
            if isinstance(post['node']['comet_sections']['content']['story']['comet_sections']['message'], dict)
        ];
        next_cursor = response['data']['node']['timeline_feed_units']['page_info']['end_cursor'];
        return posts, next_cursor;

if __name__ == '__main__':
    from dotenv import load_dotenv;
    load_dotenv();

    # Gunn Confessions
    # page_getter = PageGetter('1792991304081448', '4130381023661578');

    # Test confessions page
    page_getter = PageGetter('634679850309851', '4130381023661578');

    posts, next_cursor = page_getter.get_page();
    print('\n\n'.join(map(repr, posts)));
    posts, next_cursor = page_getter.get_page(cursor=next_cursor, count=50);
    print(len(posts));
    # print('\n\n'.join(map(repr, posts)));
    print(next_cursor);
