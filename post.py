import re

confession_number_regex = r'(?:^|\n)(\d+)\. '

class Post:
    def __init__(self, post_id, content, timestamp, comments, reactions):
        self.post_id = post_id
        self.content = content
        self.timestamp = timestamp
        self.comments = comments
        self.reactions = reactions

    def conf_num(self):
        confession_number_match = re.search(confession_number_regex, self.content)
        return int(confession_number_match.group(1)) if confession_number_match else None

    def serialize(self):
        return {
            'post_id': self.post_id,
            'content': self.content,
            'timestamp': self.timestamp,
            'comments': self.comments,
            'reactions': self.reactions
        }

    def __repr__(self):
        return 'Post(%s, %s, %s, %s, %s)' % (self.post_id, self.content, self.timestamp, self.comments, self.reactions)

def deserialize(json):
    return Post(
        json['post_id'],
        json['content'],
        json['timestamp'],
        json['comments'],
        json['reactions']
    )

def make_id_map(posts):
    return {post.conf_num(): post for post in posts}
