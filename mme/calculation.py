from PIL import Image, ImageFont, ImageDraw
from math import radians, cos, sin, asin
import re
import codecs
import json
from base64 import  b64encode
import os
from enum import Enum
from tqdm import tqdm


class MME():


    def __init__(self, profile='eng'):
        self.profile = profile
        self.points = dict()


    def load_data(self):
        points = dict()
        file = os.path.join('profiles', self.profile, 'map.json')
        if os.path.isfile(file):
            with codecs.open(file, 'r', 'utf-8') as f:
                points = json.load(f)
        self.points = points


    def load_custom_data(self):
        points = dict()
        file = os.path.join('profiles', self.profile, 'custom.json')
        if os.path.isfile(file):
            with codecs.open(file, 'r', 'utf-8') as f:
                points = json.load(f)
        for key, value in points.items():
            if key in self.points:
                self.points[key] = self.points[key] | points[key]


    def save_custom_data(self):
        points = dict()
        for key, values in self.points.items():
            status = self.points[key].get('status', 0)
            comment = self.points[key].get('comment', '')
            if status != 0 or comment != '':
                points[key] = {
                    'status': self.points[key].get('status', 0),
                    'comment' : self.points[key].get('comment', '')
                }
        file = os.path.join('profiles', self.profile, 'custom.json')
        with codecs.open(file, 'w', 'utf-8') as f:
            json.dump(points, f, ensure_ascii=False, indent=4)


    def save_data(self):
        points = dict()
        for key, values in self.points.items():
            x = self.points[key].get('x', 0)
            x = self.points[key].get('y', 0)
            z = self.points[key].get('z', 0)
            img = self.points[key].get('img', '')
            description = self.points[key].get('description', '')
            if True:
                points[key] = {
                    'x': self.points[key].get('x', 0),
                    'y': self.points[key].get('y', 0),
                    'z': self.points[key].get('z', 0),
                    'img': self.points[key].get('img', ''),
                    'description': self.points[key].get('description', '')
                }
        file = os.path.join('profiles', self.profile, 'map.json')
        with codecs.open(file, 'w', 'utf-8') as f:
            json.dump(points, f, ensure_ascii=False, indent=4)


    def __convert_coordinates_visual2abstract(self, x: int, y: int):
        src_x  = x; src_y  = y
        src_x_max = 300000; src_y_max = 350000
        src_x_delta = 125000; src_y_delta = 220000
        x = round(100 * (src_x + src_x_delta) / src_x_max, 2)
        y = round(100 * (src_y_max - (src_y_delta - src_y) ) / src_y_max, 2)

        return x, y


    def __convert_coords_abstract2picture(self, x: float, y: float, target_size: tuple):
        src_x  = x; src_y  = y
        src_x_max, src_y_max =  target_size
        x = (src_x / 100.00) * src_x_max
        y = src_y_max - (src_y / 100.00) * src_y_max

        return x, y


    def build_map(self, filter_level: int=5, marked_points: list=[]):
        img = Image.open('map.layout')
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('font.ttf', 24, encoding='UTF-8')
        self.load_data()
        for key in list(self.points.keys()):
            if int(self.points[key].get('z')) > filter_level:
                del self.points[key]
        self.load_custom_data()
        for key, values in self.points.items():
            s = int(values.get('status', 0))
            match s:
                case 1:
                    c = (76,255,0)
                case 2:
                    c = (0,255,255)
                case 3:
                    c = (255,38,38)
                case _:
                    c = (255,241,155)
            x, y = self.__convert_coords_abstract2picture(float(values.get('x')), float(values.get('y')), img.size)
            draw.ellipse((x-3, y-3, x+3, y+3))
            draw.text((x, y), key, c, font=font)
            if key in marked_points:
                draw.ellipse((x-100, y-100, x+100, y+100), outline=(255,38,38), width=3)
        img.save('map.jpg')
        with codecs.open('map.jpg', 'rb') as f:
            data = b64encode(f.read()).decode('utf-8')
        self.img = f'data:image/jpg;base64, {data}'
        return self.img


    def __distance_haversine(self, point_1: tuple, point_2: tuple):
        d_earth = 2.0 * 6372.8
        lat1, long1 = tuple(radians(c) for c in point_1)
        lat2, long2 = tuple(radians(c) for c in point_2)
        d = sin((lat2 - lat1) / 2.0) ** 2.0 + cos(lat1) * cos(lat2) * sin(
            (long2 - long1) / 2.0) ** 2.0

        return d_earth * asin(d ** 0.5)


    def __find_nearest(self, point_1: tuple):
        points = self.points
        dists = {p: self.__distance_haversine(point_1, (points[p]['x'], points[p]['y'])) for p in points}
        name, dist = min(dists.items(), key=lambda d: d[1])

        return {'name': name, 'distance': dist,
                'dist_coef': 3 if dist <= 1.0 else 2 if dist < 2.0 else 1}


    def find_point_by_coordinats(self, query: tuple):
        name = self.__find_nearest(query)['name']

        return name


    def __find_description(self, name: str):
        path = os.path.join('..', 'third_party', f'Morrowind Reference ({self.profile})')
        if not os.path.isdir(path):
            print('NO REFERENCE INSTALLED')
            return ''
        files = os.listdir(os.path.join(path, 'html'))
        _name = re.sub('(.*)(\,)(.*)', r'\1', name).replace(':', '').strip().lower()
        result = sorted(list(filter(lambda x: re.sub('(.*)(\,)|(\(локация\))|(\(Morrowind\))|(\.html)(.*)', r'\1', x).replace('_', ' ').strip().lower() == _name, files)))
        # result = sorted(list(filter(lambda x: x.startswith(name.replace(' ', '_')), files)))
        if len(result) == 0:
            return ''
        else:
            file = result[0]
        filename = os.path.join(path, 'html', file)
        if filename:
            with codecs.open(filename, 'r', 'utf-8') as f:
                description = f.read()
            description = re.sub(r'(<a.*\">)(.*)(<\/a>)', r'\2', description, flags=re.MULTILINE)
        else:
            print('NO LOCATION DESCRIPTION')
            description = 'NO LOCATION DESCRIPTION'

        return description


    def get_point_info(self, name: str):
        x = self.points[name].get('x', 0)
        y = self.points[name].get('y', 0)
        z = self.points[name].get('z', 0)
        status = self.points[name].get('status', 0)
        comment = self.points[name].get('comment', '')
        description = self.points[name].get('description', '')

        return name, x, y, z, status, comment, description


    def find_points_by_text(self, query: str=''):
        result = dict()
        for key, values in self.points.items():
            if query.strip().lower() in key.lower():
                result[key] = self.points[key]

        return result


    def convert_data(self, no_images=True):
        db_filename = os.path.join('..', 'third_party', f'mwmain_{self.profile}.gdb')
        if not os.path.isfile(db_filename):
            print(f'!Source gdb not found at: {db_filename}')
        with codecs.open(db_filename, 'r', 'utf-8') as f:
            source = f.read()
        pattern = r'(.^loc)(.*?)(nm = )(.*?)(pc = )(.*?)(lt = )(.*?)(dl = )(.*?)(np = )(.*?)(ps = )(.*?)(pd = )(.*?)(,)(.*?)(pt = )(.*?)(.^end)'
        result = re.findall(pattern, source, flags=re.MULTILINE|re.DOTALL)
        self.points = dict()
        for item in result:
            name = item[3].strip()
            x, y = self.__convert_coordinates_visual2abstract(int(item[15].strip()), int(item[17].strip()))
            z = int(item[9].strip())
            self.points[name] = {'x': x, 'y': y, 'z': z}
        self.points = dict(sorted(self.points.items()))
        for key in tqdm(self.points.keys()):
            description = self.__find_description(key)
            if description == 'NO LOCATION DESCRIPTION':
                print(f'!NO DESCRIPTION for {key}')
            pattern = r'(<img)(.*?)(src=")(.*?)(")(.*?)(>)'
            result = re.findall(pattern, description, flags=re.MULTILINE|re.DOTALL)
            if no_images:
                description = re.sub(pattern, '', description)
            self.points[key]['img'] = ''
            self.points[key]['description'] = description
        self.save_data()


    def patch_data(self):
        patch = dict()
        report = ''
        file = os.path.join('profiles', self.profile, 'patch.json')
        if os.path.isfile(file):
            with codecs.open(file, 'r', 'utf-8') as f:
                patch = json.load(f)
        self.load_data()
        for orig_name, value in patch.items():
            patch_data = patch[orig_name]
            if orig_name in self.points:
                n = patch_data.get('n', None) if patch_data.get('n', None) else self.points[orig_name].get('n')
                x = patch_data.get('x', None) if patch_data.get('x', None) else self.points[orig_name].get('x')
                y = patch_data.get('y', None) if patch_data.get('y', None) else self.points[orig_name].get('y')
                z = patch_data.get('z', None) if patch_data.get('z', None) else self.points[orig_name].get('z')
                del self.points[orig_name]
                self.points[n] = {'x': x, 'y': y, 'z': z}
                report += f'!MODIFIED: {orig_name} => {n} {self.points[n]}\n'
            else:
                n = patch_data.get('n', None) if patch_data.get('n', None) else 'NEW LOCATION NAME'
                x = patch_data.get('x', None) if patch_data.get('x', None) else 1
                y = patch_data.get('y', None) if patch_data.get('y', None) else 1
                z = patch_data.get('z', None) if patch_data.get('z', None) else 1
                self.points[n] = {'x': x, 'y': y, 'z': z}
                report += f'!NEW ADDED: {n} {self.points[n]}\n'
        self.points = dict(sorted(self.points.items()))
        self.save_data()
        print(report)
        return report


if __name__ == '__main__':
    ...
    # mme = MME('ru')
    # mme.convert_data()
    # mme.patch_data()
