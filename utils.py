import re

confession_number_regex = r'^(\d+)\. '

def get_confession_number(confession_text):
    confession_number_match = re.search(confession_number_regex, confession_text)
    if confession_number_match:
        return int(confession_number_match.group(1))
    else:
        return 0
