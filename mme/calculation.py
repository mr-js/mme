from PIL import Image, ImageFont, ImageDraw
from math import radians, cos, sin, asin
from difflib import SequenceMatcher
import re
import codecs
import json
from base64 import  b64encode
import os
from tqdm import tqdm


class MME():


    def __init__(self, profile='eng', filter_level=4):
        self.profile = profile
        self.filter_level = filter_level
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
            description = self.points[key].get('description', '')
            if True:
                points[key] = {
                    'x': self.points[key].get('x', 0),
                    'y': self.points[key].get('y', 0),
                    'z': self.points[key].get('z', 0),
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


    def build_map(self, marked_points: list=[]):
        img = Image.open('map.layout')
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('font.ttf', 24, encoding='UTF-8')
        self.load_data()
        for key in list(self.points.keys()):
            if int(self.points[key].get('z')) > self.filter_level:
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


    def __build_locations_coordinates(self):
        self.load_data()
        report = 'BUILDING LOCATIONS COORDINATES BEGIN\n'
        db_filename = os.path.join('..', 'third_party', f'mwmain_{self.profile}.gdb')
        if not os.path.isfile(db_filename):
            print(f'!Source gdb not found at: {db_filename}')
            return None
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
        report += 'BUILDING LOCATIONS COORDINATES END\n'
        print(report)
        self.save_data()


    def __load_description(self, filename, remove_images=False, remove_href=True):
        content = ''
        href_code_pattern=r'(<a.*\">)(.*)(<\/a>)'
        img_code_pattern = r'(<img)(.*?)(src=")(.*?)(")(.*?)(>)'
        if os.path.isfile(filename):
            with codecs.open(filename, 'r', 'utf-8') as f:
                content = f.read()
            content = re.sub(href_code_pattern, r'\2', content, flags=re.MULTILINE)
            if remove_images:
                content = re.sub(img_code_pattern, '', content)
        return content


    def __resolve_filenames(self, name, files, threshold=0.1):
        result = max(list(map(lambda x: {'file': x, 'ratio' : SequenceMatcher(None, name, x).ratio()}, files)), key=lambda x: float(x['ratio']))
        if result.get('ratio') >= threshold:
            return result.get('file')
        else:
            return ''


    def __build_locations_descriptions(self, reference_path='', ai_resolving=True, remove_images=False):
        self.load_data()
        report = 'BUILDING LOCATIONS DESCRIPTIONS BEGIN\n'
        if not reference_path:
            path = os.path.join('..', 'third_party', f'Morrowind Reference ({self.profile})')
        else:
            path = reference_path
        if not os.path.isdir(path):
            print(f'!Reference not found at: {path}')
            return None
        files = os.listdir(os.path.join(path, 'html'))
        match (self.profile):
            case 'ru':
                names_compares = lambda x, y: re.sub('(.*)(\,)|(\(локация\))|(\(Morrowind\))|(\.html)(.*)', r'\1', y).replace('_', ' ').strip().lower() == re.sub('(.*)(\,)(.*)', r'\1', x).replace(':', '').strip().lower()
            case 'eng':
                names_compares = lambda x, y: re.sub('(.*)(\,)|(\(location\))|(\(Morrowind\))|(\.html)(.*)', r'\1', y).replace('_', ' ').strip().lower() == re.sub('(.*)(\,)(.*)', r'\1', x).replace(':', '').strip().lower()
            case _:
                names_compares = lambda x, y: re.sub('(.*)(\,)|(\(location\))|(\(Morrowind\))|(\.html)(.*)', r'\1', y).replace('_', ' ').strip().lower() == re.sub('(.*)(\,)(.*)', r'\1', x).replace(':', '').strip().lower()
        for name in tqdm(self.points.keys(), desc='Building descriptions'):
            description = self.points[name].get('description', None)
            if r'<html>' in description:
                continue
            result = sorted(list(filter(lambda file: names_compares(name, file), files)))
            if len(result) == 0 and description.startswith('FILE:'):
                result = sorted(list(filter(lambda file: names_compares(description.split('FILE:')[1], file), files)))
            if len(result) == 0 and ai_resolving == True:
                result = [self.__resolve_filenames(name, files)]
            if len(result) == 0:
                report += f'!NO DESCRIPTION: {name}\n'
                continue
            filename = os.path.join(path, 'html', result[0])
            self.points[name]['description'] = self.__load_description(filename, remove_images)
        report += 'BUILDING LOCATIONS DESCRIPTIONS END\n'
        print(report)
        self.save_data()


    def patch_data(self):
        patch = dict()
        report = 'PATCHING DATA BEGIN\n'
        filename = os.path.join('profiles', self.profile, 'patch.json')
        if os.path.isfile(filename):
            with codecs.open(filename, 'r', 'utf-8') as f:
                patch = json.load(f)
        self.load_data()
        for item in list(patch):
            item_value = patch[item]
            if item.startswith('*'):
                item_name_part = item.split('*')[1]
                for point_name in list(self.points.keys()):
                    if item_name_part.lower().strip() in point_name.lower().strip():
                        if patch.get(point_name, None) is None:
                            patch[point_name] = item_value
                        else:
                            report += f'!AUTO GROUP PATCH PASSED: {point_name}'
                del patch[item]
        for name in tqdm(list(patch.keys()), desc='Patching data'):
            patch_data = patch[name]
            operation_type = ''
            if any(filter(lambda x: x == name, list(self.points.keys()))):
                n = patch_data.get('name', None) if patch_data.get('name', None) else name
                x = patch_data.get('x', None) if patch_data.get('x', None) else self.points[name].get('x')
                y = patch_data.get('y', None) if patch_data.get('y', None) else self.points[name].get('y')
                z = patch_data.get('z', None) if patch_data.get('z', None) else self.points[name].get('z')
                d = patch_data.get('description', None) if patch_data.get('description', None) else self.points[name].get('description')
                del self.points[name]
                report += f'!MODIFIED: {n}\n'
            else:
                n = patch_data.get('name', None) if patch_data.get('name', None) else name
                x = patch_data.get('x', None) if patch_data.get('x', None) else 100
                y = patch_data.get('y', None) if patch_data.get('y', None) else 100
                z = patch_data.get('z', None) if patch_data.get('z', None) else 0
                d = patch_data.get('description', None) if patch_data.get('description', None) else ''
                report += f'!ADDED: {n}\n'
            if not r'<html>' in d and d.startswith('FILE:'):
                filename= os.path.join('profiles', self.profile, d.split('FILE:')[1])
                content = self.__load_description(filename)
                d = content if content else d
            self.points[n] = {'x': x, 'y': y, 'z': z, 'description': d}
        self.points = dict(sorted(self.points.items()))
        self.save_data()
        report += 'PATCHING DATA END\n'
        print(report)
        return report


if __name__ == '__main__':
    ...
    # mme = MME('eng')
    # mme._MME__build_locations_coordinates()
    # mme.patch_data()
    # remove_images=False
    # mme._MME__build_locations_descriptions(reference_path=r'C:\Games\Morrowind [MOD]\custom\Morrowind Reference (ENG)', ai_resolving=True, remove_images=remove_images)

    # mme = MME('ru')
    # mme._MME__build_locations_coordinates()
    # mme.patch_data()
    # remove_images=True
    # mme._MME__build_locations_descriptions(reference_path=r'C:\Games\Morrowind [MOD]\custom\Morrowind Reference', ai_resolving=False, remove_images=remove_images)
