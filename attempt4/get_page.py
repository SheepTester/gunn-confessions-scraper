from urllib.parse import urlencode
import json
import requests

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
        self.content = raw_comment['body']['text'];
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

    def __repr__(self):
        return f'{repr(self.post)} comments={self.comment_count} reactions={self.reaction_count} ({" ".join(map(repr, self.reactions))}) shares={self.share_count}' \
            + ''.join('\n' + repr(comment) for comment in self.comments);

def get_page(cursor, count=3):
    body = urlencode({
        # No idea what this means, but it's needed
        'fb_dtsg': 'AQHS7sAiDqyR:AQHryv1x5_m1',

        # Presumably this refers to the Gunn Confessions page
        'doc_id': '4130381023661578',

        'variables': json.dumps({
            'count': count,
            'cursor': cursor,

            # Needed for comments to be listed
            'feedLocation': 'PAGE_TIMELINE',

            # If omitted, Facebook gives a warning about it being omitted
            'privacySelectorRenderLocation': 'COMET_STREAM',

            # Not sure what this is an ID for
            'id': '1792991304081448',
        }),
    });
    response = requests.post(
        'https://www.facebook.com/api/graphql/',
        data=body,
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    ).json();
    posts = [
        Post(post)
        for post in response['data']['node']['timeline_feed_units']['edges']
    ];
    next_cursor = response['data']['node']['timeline_feed_units']['page_info']['end_cursor'];
    return posts, next_cursor;

if __name__ == '__main__':
    posts, next_cursor = get_page('AQHRL2j5XiIzM7fAzUHHJ7DQ_MItv0J99qXmJIqBrPrMaiQha8EXzktfiJww3vsXwYvRurRrTFwN7p4od0nVgZD27en9hNJ8JVxkF_xjm6ml1yIkBZlbrY1FKSj1xwyCfhII');
    print('\n\n'.join(map(repr, posts)));
    posts, next_cursor = get_page(next_cursor);
    print('\n\n'.join(map(repr, posts)));
    print(next_cursor);
