from PIL import Image
import json
import post
import math
from datetime import datetime

WIDTH = 1000

def create_missing_visual(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        confessions = post.make_id_map([post.deserialize(item) for item in json.loads(file.read())])

    max_conf = max(confessions.keys())

    data = [0] * max_conf
    for confession in range(0, max_conf):
        data[confession] = 0 if confession + 1 in confessions else 1

    # https://stackoverflow.com/a/435215
    image = Image.new('1', (WIDTH, math.ceil(max_conf / WIDTH)))
    image.putdata(data)
    save_target = './output/missing_%s.png' % datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
    image.save(save_target)
    print('Saved missing confession visualization in %s' % save_target)
    return save_target

if __name__ == '__main__':
    create_missing_visual('./output-dist/2020-06-15.json')
