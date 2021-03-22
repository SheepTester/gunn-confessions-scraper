# Based on draw_missing.py

from PIL import Image;
from yaml import safe_load;
from datetime import datetime;

WIDTH = 100;
THOUSAND = 1000;

colours = {
    'empty': (0, 0, 0),
    'found': (200, 200, 200),
    'found_alt': (220, 220, 220),
    'missing': (200, 50, 50),
    'missing_alt': (220, 50, 50),
};

confession_number_regex = r'(?:^|\n)(\d+)\.\s';

def get_confession_id(confession):
    confession_number_match = re.search(confession_number_regex, confession['content']);
    return int(confession_number_match.group(1));

def create_missing_visual(found_path):
    with open(found_path, 'r', encoding='utf-8') as file:
        confessions = safe_load(found);
    confession_ids = map(get_confession_id, confessions);
    max_confession_id = max(confession_ids);

    data = [colours['empty']] * max_confession_id;
    for confession_id in range(1, max_confession_id):
        colour = 'found' if confession_id in confession_ids else 'missing';
        thousands = math.floor(confession_id / THOUSAND);
        data[confession_id] = colours[colour if thousands % 2 == 0 else colour + '_alt'];

    # https://stackoverflow.com/a/435215
    image = Image.new('RGB', (WIDTH, math.ceil(max_conf / WIDTH)), colours['empty']);
    image.putdata(data);
    save_target = f'./output/a4_missing_{datetime.now().strftime("%Y-%m-%d_%H.%M.%S")}.png';
    image.save(save_target);
    print(f'Saved missing confession visualization in {save_target}');
    return save_target;

if __name__ == '__main__':
    create_missing_visual('./output-dist/a4_2021-03-21_22.43.46.yml');
