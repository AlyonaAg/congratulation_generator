import re
import requests
import difflib
from random import randint

word_dict = {}
ratio_dict = {}

url = 'http://imgpng.ru'


def get_image_from_category(top_category, count):
    reg = r"src=\"(//pngimg\.com/uploads[\/\w\.]+)"
    name_list = []

    req1 = requests.get(url + word_dict[top_category]).text
    find_image = re.findall(reg, req1)

    for _ in range(count):
        req2 = requests.get('http:' + find_image[randint(0, len(find_image) - 1)])
        name = str(randint(0, 1000)) + '.png'
        name_list.append(name)
        with open(name, 'wb') as f:
            f.write(req2.content)

    return name_list


def get_category(text, count):
    def compare(s1, s2):
        s1 = s1.lower().split(" ")
        s2 = s2.lower()
        ratio_dict[s2] = max(difflib.SequenceMatcher(None, part_s1, s2).ratio()
                             for part_s1 in s1 if len(part_s1) > 2)

    reg = r"<a href=\"(\/img\/\w+\/\w+)\">([\w,\s]+)<\/a>"

    req = requests.get(url).text
    find_category = re.findall(reg, req)

    for category in find_category:
        word_dict[category[1].lower()] = category[0]
        compare(text, category[1])
    top_category = sorted(ratio_dict.items(), key=lambda x: x[1], reverse=True)[0][0]
    return get_image_from_category(top_category, count)
