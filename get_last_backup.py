import re
import json
from datetime import datetime

def get_last_backup(backup_name):
    with open(backup_name, 'r', encoding='utf-8') as file:
        backup = file.read()

    backups = re.split(r'(?<=\n\])(?=\[)', backup)
    print('%d backup(s) were in that file' % len(backups))

    filename = './output/last_backup_%s.json' % datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(backups[-1])
    print('Saved last backup to %s' % filename)
    return filename

def merge_all_backups(backup_name):
    with open(backup_name, 'r', encoding='utf-8') as file:
        backup_file = file.read()

    backups = re.split(r'(?<=\}|\])\r?\n(?=\[|\{)', backup_file)
    print('%d backup(s) were in that file' % len(backups))

    merged = {}
    for backup in backups:
        merged.update(json.loads(backup))

    # Sort keys
    merged = dict(sorted(merged.items(), key=lambda pair: int(pair[0]) if pair[0] != 'null' else 0))

    filename = './output/merged_backup_%s.json' % datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(json.dumps(merged, indent=2))
    print('Saved merged backup to %s' % filename)
    return filename

if __name__ == '__main__':
    get_last_backup('./output/_posts_fetch_missing.json')
    # merge_all_backups('./output/userscript_logs_2020-06-16.json')
