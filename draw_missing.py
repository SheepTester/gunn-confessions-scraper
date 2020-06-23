from PIL import Image
import json
import post
import math
from datetime import datetime

WIDTH = 100
THOUSAND = 1000

colours = {
    'empty': (0, 0, 0),
    'found': (200, 200, 200),
    'found_alt': (220, 220, 220),
    'missing': (200, 50, 50),
    'missing_alt': (220, 50, 50),
    'truly_missing': (100, 50, 50),
    'truly_missing_alt': (120, 50, 50),
    'has_post_id': (50, 150, 200),
    'has_post_id_alt': (50, 170, 220),
}

def create_missing_visual(found=None, searched=None, spreadsheet=None):
    if found:
        with open(found, 'r', encoding='utf-8') as file:
            confessions = post.make_id_map([post.deserialize(item) for item in json.loads(file.read())])
        max_conf = max(confessions.keys())
    else:
        confessions = {}
        max_conf = 1

    if searched:
        with open(searched, 'r', encoding='utf-8') as file:
            has_post_id = set(int(num) for num in json.loads(file.read()).keys() if num != 'null' and not num.startswith('worrying'))
    else:
        has_post_id = set()

    if spreadsheet:
        with open(spreadsheet, 'r', encoding='utf-8') as file:
            truly_missing = set(i + 1 for i, line in enumerate(file) if line.strip() == '')
    else:
        truly_missing = set()

    data = [colours['empty']] * max_conf
    for confession in range(1, max_conf):
        num = confession
        colour = 'found' if num in confessions else 'has_post_id' if num in has_post_id else 'truly_missing' if num in truly_missing else 'missing'
        thousands = math.floor(num / THOUSAND)
        data[confession] = colours[colour if thousands % 2 == 0 else colour + '_alt']

    # https://stackoverflow.com/a/435215
    image = Image.new('RGB', (WIDTH, math.ceil(max_conf / WIDTH)), colours['empty'])
    image.putdata(data)
    save_target = './output/missing_%s.png' % datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
    image.save(save_target)
    print('Saved missing confession visualization in %s' % save_target)
    return save_target

if __name__ == '__main__':
    # https://docs.google.com/spreadsheets/d/e/2PACX-1vTJMHCAsgqtErQGbQyXs_UObhWllWCdEbKAQ5U2_zzE1XGL5FgTaLbXMjrbUOVTR4uzZAMyfMGFmShY/pub?gid=0&single=true&output=tsv
    create_missing_visual(
        found='./output-dist/2020-06-15.json',
        searched='./output/userscript_2020-06-23.json',
        spreadsheet='./output/posts.tsv'
    )
