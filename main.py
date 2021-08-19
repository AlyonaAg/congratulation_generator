from PIL import Image
from html2image import Html2Image
from pythonWordArt import *
from random import randint, uniform
from sys import argv
import shutil
import re
import requests
import difflib
import os


def search_boundaries(data, size):
    width, height = 0, 0
    width_min, height_min, width_max, height_max = \
        size[0], size[1], 0, 0

    for item in data:
        width += 1
        if width == size[0]:
            width = 0
            height += 1

        if item[0] != 255 or item[1] != 255 or item[2] != 255:
            if width > width_max:
                width_max = width
            elif width < width_min:
                width_min = width

            if height > height_max:
                height_max = height
            elif height < height_min:
                height_min = height

    return (width_min, height_min, width_max, height_max)


def remove_background(data):
    new_data = []
    for item in data:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    return new_data


class Congratulation:
    def __init__(self):
        self.background = None
        self.textPNG = None
        self.text = ''
        self.min_indent = 30
        self.wordArt = pyWordArt()
        self.word_dict = {}
        self.ratio_dict = {}
        self.url_png = 'http://imgpng.ru'

        self.Style = {
            'outline': 0,
            'up': 1,
            'arc': 2,
            'squeeze': 3,
            'inverted-arc': 4,
            'italic-outline': 6,
            'slate': 7,
            'mauve': 8,
            'graydient': 9,
            'red-blue': 10,
            'radial': 12,
            'purple': 13,
            'green-marble': 14,
            'rainbow': 15,
            'aqua': 16,
            'paper-bag': 18,
            'sunset': 19,
            'tilt': 20,
            'blues': 21,
            'yellow-dash': 22,
            'chrome': 24,
            'marble-slab': 25,
            'gray-block': 26,
            'superhero': 27,
            'horizon': 28,
        }

    def create_background(self, path=None):
        while True:
            self.get_background()
            self.background = Image.open('./temp/sample.jpg')
            if self.background.size[0] >= self.background.size[1]:
                if self.background.size[0] > 1280:
                    maxsize = (1280, 1280)
                    self.background.thumbnail(maxsize, Image.ANTIALIAS)
                break
            self.background.close()

    def create_text(self, text='С праздником!', size=100, filename='temp.png'):
        self.text = text
        if len(text) > 50:
            self.exception(type_except='longtext')

        hti = Html2Image(output_path='./temp/')
        style = list(self.Style.keys())[randint(0, len(self.Style) - 1)]
        html_page = self.wordArt.toHTML(text, self.wordArt.Styles[style], size)

        with open('./temp/temp.html', 'w') as f:
            f.write(html_page)
        hti.screenshot(html_file='./temp/temp.html', save_as=filename)

        self.textPNG = Image.open('./temp/' + filename)
        self.textPNG = self.textPNG.convert("RGBA")
        data = self.textPNG.getdata()
        self.textPNG.putdata(remove_background(data))
        self.textPNG = self.textPNG.crop(search_boundaries(data, self.textPNG.size))

    def image_resize(self, im, scaling=3):
        side_scaling = 0 if im.size[0] > im.size[1] else 1

        try:
            desired_side1 = int(self.background.size[side_scaling] // scaling)
            percent = (desired_side1 / float(im.size[side_scaling]))
            desired_side2 = int((float(im.size[1 - side_scaling]) * float(percent)))
        except ZeroDivisionError:
            self.exception()

        if side_scaling == 0:
            im = im.resize((desired_side1, desired_side2), Image.ANTIALIAS)
        else:
            im = im.resize((desired_side2, desired_side1), Image.ANTIALIAS)

        return im

    def paste_text(self):
        self.textPNG = self.image_resize(self.textPNG, scaling=1.1)
        height = randint(self.min_indent,
                         self.background.size[1] - self.min_indent - self.textPNG.size[1])
        weight = randint(self.min_indent,
                         self.background.size[0] - self.min_indent - self.textPNG.size[0])

        self.background.paste(self.textPNG, (weight, height), mask=self.textPNG)

    def paste_add_png(self):
        name_list = self.get_category(self.text)
        for name in name_list:
            im = Image.open(name)
            im = self.image_resize(im, scaling=uniform(2, 3))
            height = randint(self.min_indent,
                             self.background.size[1] - self.min_indent * 2)
            weight = randint(self.min_indent,
                             self.background.size[0] - self.min_indent * 2)

            try:
                self.background.paste(im, (weight, height), mask=im)
            except ValueError:
                print('bad image.... skip...')
            im.close()

    def create_image(self, text, min_indent=30, size=80):
        if os.path.exists('./temp'):
            shutil.rmtree('./temp')
        os.mkdir('./temp')
        os.system('attrib +h ./temp')
        self.min_indent = min_indent
        self.create_background()
        self.create_text(text, size=size)
        self.paste_add_png()
        self.paste_text()

    def exception(self, type_except='unknown'):
        if type_except == 'longtext':
            path = './exception/long text/'
        elif type_except == 'connect':
            path = './exception/connect/'
        else:
            path = './exception/unknown bug/'

        files = os.listdir(path=path)
        self.background = Image.open(path + files[randint(0, len(files) - 1)])
        self.save_image()
        self.finality()
        exit(-1)

    def get_image_from_category(self, top_category):
        reg = r"src=\"(//pngimg\.com/uploads[\/\w\.]+)"
        name_list = []

        for category in top_category:
            req1 = requests.get(self.url_png + self.word_dict[category[0]]).text
            find_image = re.findall(reg, req1)

            for _ in range(randint(0, 3)):
                req2 = requests.get('http:' + find_image[randint(0, len(find_image) - 1)])
                name = './temp/' + str(randint(0, 1000)) + '.png'
                name_list.append(name)
                with open(name, 'wb') as f:
                    f.write(req2.content)
        return name_list

    def get_category(self, text):
        def compare(s1, s2):
            s1 = s1.lower().split(" ")
            s2 = s2.lower()
            self.ratio_dict[s2] = max(difflib.SequenceMatcher(None, part_s1, s2).ratio()
                                 for part_s1 in s1 if len(part_s1) > 2)

        reg = r"<a href=\"(\/img\/\w+\/\w+)\">([\w,\s]+)<\/a>"
        req = requests.get(self.url_png).text
        find_category = re.findall(reg, req)
        if len(find_category) == 0:
            self.exception('connect')

        for category in find_category:
            self.word_dict[category[1].lower()] = category[0]
            compare(text, category[1])
        top_category = sorted(self.ratio_dict.items(), key=lambda x: x[1], reverse=True)[:3]
        print(top_category)
        return self.get_image_from_category(top_category)

    def get_background(self):
        print('get')
        reg = r"https:\/\/pixabay\.com\/get\/.*?\.jpg"
        req1 = requests.get('https://www.generatormix.com/random-image-generator')
        with open('./temp/sample.jpg', 'wb') as f:
            req2 = re.findall(reg, req1.text)
            if len(req2):
                f.write(requests.get(req2[0]).content)
            else:
                self.exception('connect')

    def save_image(self, output='output.jpg'):
        self.background.save(output)

    def finality(self):
        shutil.rmtree('./temp')
        self.background.close()


if __name__ == '__main__':
    if len(argv) > 1:
        congr = Congratulation()
        try:
            congr.create_image(' '.join(argv[1:]).strip("\'\""), size=80)
            congr.save_image()
        except:
            congr.exception()
        finally:
            congr.finality()
