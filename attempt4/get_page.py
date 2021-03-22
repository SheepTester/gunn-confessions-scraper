import os;
from datetime import datetime;
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

    def yaml(self, indent=''):
        yaml = indent + f'- author: {self.author}\n';
        yaml += indent + f'  content: {json.dumps(self.content, ensure_ascii=False)}\n';
        yaml += indent + f'  created: {self.created}\n';
        yaml += indent + f'  author-url: {self.author_url}\n';
        return yaml;

class Post:
    def __init__(self, raw_post):
        sections = raw_post['node']['comet_sections'];
        feedback = sections['feedback']['story']['feedback_context']['feedback_target_with_context'];

        self.content = sections['content']['story']['comet_sections']['message']['story']['message']['text'];
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
        return f'{repr(self.content)} comments={self.comment_count} reactions={self.reaction_count} ({" ".join(map(repr, self.reactions))}) shares={self.share_count}' \
            + ''.join('\n' + repr(comment) for comment in self.comments);

    def yaml(self, indent=''):
        yaml = indent + f'- content: {json.dumps(self.content, ensure_ascii=False)}\n';
        reactions = {};
        for reaction in self.reactions:
            reactions[reaction.type] = reaction.count;
        # I'm too used to Standard.JS now
        reactions = '{ %s }' % json.dumps(reactions)[1:-1] if len(self.reactions) > 0 else '{}';
        yaml += indent + f'  reactions: {reactions}\n';
        yaml += indent + f'  comments:';
        if len(self.comments) > 0:
            yaml += '\n';
            for comment in self.comments:
                yaml += comment.yaml(indent=indent + '  ');
        else:
            yaml += ' []\n';
        yaml += indent + f'  created: {self.created}\n';
        yaml += indent + f'  url: {self.url}\n';
        return yaml;

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
        page, which may be None if you're on the last page.
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
        page_info = response['data']['node']['timeline_feed_units']['page_info'];
        next_cursor = page_info['end_cursor'] if page_info['has_next_page'] else None;
        return posts, next_cursor;

if __name__ == '__main__':
    from dotenv import load_dotenv;
    load_dotenv();

    # Gunn Confessions
    # page_getter = PageGetter('1792991304081448', '4130381023661578');

    # Test confessions page
    page_getter = PageGetter('634679850309851', '4130381023661578');

    time = datetime.now().strftime('%Y-%m-%d_%H.%M.%S');
    with open(f'./output/a4_{time}.yml', 'a', encoding='utf8') as file:
        cursor = None;
        while True:
            posts, cursor = page_getter.get_page(cursor, count=297);
            file.write('\n'.join(post.yaml() for post in posts));
            if cursor is None:
                break;
            else:
                print(cursor);
        print('Done! :D');
