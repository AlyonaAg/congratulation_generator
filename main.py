from PIL import Image
from html2image import Html2Image
from pythonWordArt import *
from random import randint
import os
import requests
import re
import html_parser


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
            get_background()
            self.background = Image.open('sample.jpg')
            print(self.background.size)
            if self.background.size[0] >= self.background.size[1]:
                if self.background.size[0] > 1280:
                    maxsize = (1280, 1280)
                    self.background.thumbnail(maxsize, Image.ANTIALIAS)
                break
            self.background.close()
            os.remove('sample.jpg')

    def create_text(self, text='С праздником!', style=None, size=100):
        self.text = text
        if len(text) > 50:
            print('Текст слишком длинный (>50).')
            # бросить исключение потом
            exit(-1)

        hti = Html2Image()
        w = pyWordArt()

        if style is None:
            number_style = randint(0, len(self.Style) - 1)
            style = list(self.Style.keys())[number_style]

        html_page = w.toHTML(text, w.Styles[style], size)
        #исключение на неизвестный стиль

        with open('temp.html', 'w') as f:
            os.system('attrib +h temp.html')
            f.write(html_page)
        hti.screenshot(html_file='temp.html', save_as='temp.png')
        os.system('attrib +h temp.png')

        self.textPNG = Image.open('temp.png')
        self.textPNG = self.textPNG.convert("RGBA")
        data = self.textPNG.getdata()
        self.textPNG.putdata(remove_background(data))
        self.textPNG = self.textPNG.crop(search_boundaries(data, self.textPNG.size))

    def image_resize(self, im, scaling=3):
        if im.size[0] > im.size[1]:
            side_scaling = 0
        else:
            side_scaling = 1

        desired_side1 = int(self.background.size[side_scaling] // scaling)
        percent = (desired_side1 / float(im.size[side_scaling]))
        desired_side2 = int((float(im.size[1 - side_scaling]) * float(percent)))

        if side_scaling == 0:
            im = im.resize((desired_side1, desired_side2), Image.ANTIALIAS)
        else:
            im = im.resize((desired_side2, desired_side1), Image.ANTIALIAS)
        return im

    def paste_text(self):
        min_indent = 30

        self.textPNG = self.image_resize(self.textPNG, scaling=1.1)
        height = randint(min_indent,
                         self.background.size[1] - min_indent - self.textPNG.size[1])
        weight = randint(min_indent,
                         self.background.size[0] - min_indent - self.textPNG.size[0])

        try:
            self.background.paste(self.textPNG, (weight, height), mask=self.textPNG)
        except:
            print('height: ', height)
            print('weight: ', weight)
            print('background: ', self.background)
            print('textPNG: ', self.textPNG)

    def paste_add_png(self):
        min_indent = 30
        count_png = randint(1, 4)

        name_list = html_parser.get_category(self.text, count_png)
        for name in name_list:
            im = Image.open(name)
            im = self.image_resize(im, scaling=2.5)
            height = randint(min_indent,
                             self.background.size[1] - min_indent - im.size[1])
            weight = randint(min_indent,
                             self.background.size[0] - min_indent - im.size[0])

            self.background.paste(im, (weight, height), mask=im)
            im.close()

    def save_image(self, output='output.jpg'):
        self.background.save(output)


if __name__ == '__main__':
    congr = Congratulation()
    try:
        congr.create_background()
        congr.create_text('С днём отсутсвия горячей воды! С днём', size=80)
        congr.paste_add_png()
        congr.paste_text()
        congr.save_image()
    finally:
        os.remove('sample.jpg')
        os.remove('temp.html')
        os.remove('temp.png')