import re
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

if __name__ == '__main__':
    get_last_backup('./output/_posts_fetch_missing.json')
