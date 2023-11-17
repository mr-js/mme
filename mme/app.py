from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from markupsafe import Markup, escape
from waitress import serve
import time
from secrets import token_hex
import webbrowser
import pathlib
import json
import codecs
import os
from calculation import MME
from itertools import cycle


app = Flask(__name__)
app.secret_key = token_hex(16)
filter_level = 4
mme = MME()
settings = dict()


def load_global_settings():
    global settings
    if os.path.isfile('settings.json'):
        with codecs.open('settings.json', 'r', 'utf-8') as f:
            settings = json.load(f)
    if 'ui' not in settings:
        settings['ui'] = {'languages' : {'ru', 'eng'}}
        settings['ui'] = {'language' : 'ru'}
    mme.profile = settings['ui']['language']
    if 'view_point' not in settings:
        settings['view_point'] = {'x' : 0, 'y' : 0, 'z' : 100}


def save_global_settings():
    global settings
    with codecs.open('settings.json', 'w', 'utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)


def __next_language():
    languages_cycle = cycle(settings['ui']['languages'])
    while (limit := 0 < 10):
        limit += 1
        item = next(languages_cycle)
        if item == settings['ui']['language']:
            settings['ui']['language'] = next(languages_cycle)
            return settings['ui']['language']


@app.route('/', methods=['POST', 'GET'])
def page_main():
    global mme
    load_global_settings()
    mme.build_map(filter_level)
    report = ''
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        save_global_settings()
        if request.form['action'] == 'Language':
            __next_language()
            save_global_settings()
            load_global_settings()
            mme.build_map(filter_level)
        elif request.form['action'] == 'Patch':
            report = mme.patch_data()
            mme.build_map(filter_level)
    names = mme.find_points_by_text('')

    return render_template('main.html', img=mme.img, names=names, settings=settings, report=report)


@app.get('/map_init')
def map_init():
    return jsonify(view_point=settings['view_point'])


@app.get('/map_clicked')
def map_clicked():
    global mme
    x_rel = float(request.args.get('x_rel'))
    y_rel = float(request.args.get('y_rel'))
    name = mme.find_point_by_coordinats((x_rel, y_rel))
    name, x, y, z, status, comment, description = mme.get_point_info(name)

    return jsonify(name=name, status=status, comment=comment, description=description)


@app.get('/map_moved')
def map_moved():
    global settings
    settings['view_point'] = {
        'x': int(request.args.get('x')),
        'y': int(request.args.get('y')),
        'z': int(request.args.get('z')),
    }
    save_global_settings()
    return jsonify(comment=settings['view_point'])


@app.get('/update_custom_data')
def update_custom_data():
    global mme
    name = request.args.get('name')
    status = int(request.args.get('status'))
    comment = request.args.get('comment')
    if name in mme.points.keys():
        mme.points[name].update({'status' : status})
        mme.points[name].update({'comment' : comment})
        mme.save_custom_data()
    # load_global_settings()
    img = mme.build_map(filter_level)
    return jsonify(img=img)


@app.get('/search_clicked')
def search_clicked():
    global mme
    report = 'Search results:\n'
    text = request.args.get('text')
    results = mme.find_points_by_text(text)
    img = mme.build_map(filter_level, results)
    report += '\n'.join(f'{k}\t[{v.get("x")}:{v.get("y")}]' for k, v in results.items())
    return jsonify(img=img, text=text, report=report)

if __name__ == '__main__':
    # app.run(host='0.0.0.0', debug=True, port='5000')
    webbrowser.open('http://127.0.0.1:8080')
    serve(app, host="0.0.0.0", port=8080)
