from post import make_id_map, deserialize
import json

def load_confessions(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return [deserialize(item) for item in json.loads(file.read())]

def sort_longest(confessions):
    copy = confessions.copy()
    copy.sort(key=lambda confession: len(confession.content), reverse=True)
    return copy

if __name__ == '__main__':
    confs = load_confessions('./output-dist/last_backup_2020-06-15_18.08.37.json')
    confs_by_id = make_id_map(confs)

    longest = sort_longest(confs)
    # print('\n\n'.join(map(lambda conf: conf.content, longest[:5])))
    print('\n'.join(['#%d: %d (%d chars)%s' % (i + 1, conf.conf_num(), len(conf.content), ' - https://www.facebook.com/gunnconfessions/posts/%s' % conf.post_id if i < 5 else '') for i, conf in enumerate(longest[:20])]))
