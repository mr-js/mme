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


app = Flask(__name__)
app.secret_key = token_hex(16)
filter_level = 4
mme = MME(filter_level)
settings = dict()


def load_global_settings():
    global settings
    if os.path.isfile('settings.json'):
        with codecs.open('settings.json', 'r', 'utf-8') as f:
            settings = json.load(f)
    if 'view_point' not in settings:
        settings['view_point'] = {'x' : 0, 'y' : 0, 'z' : 100}
    if 'search' not in settings:
        settings['search'] = {'text' : '', 'results' : {}}


def save_global_settings():
    global settings
    with codecs.open('settings.json', 'w', 'utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)


def find(text=''):
    report = 'Search results:\n'
    if text != '':
        settings['search'] = dict()
        settings['search']['text'] = text
        settings['search']['results'] = mme.find_points_by_text(text)
    else:
        settings['search'] = dict()
        settings['search']['text'] = ''
        settings['search']['results'] = dict()
    report += '\n'.join(f'{k}\t[{v.get("x")}:{v.get("y")}]' for k, v in settings['search']['results'].items())

    return report


@app.route('/', methods=['POST', 'GET'])
def page_main():
    global mme
    load_global_settings()
    mme.build_map(filter_level, settings['search']['results'])
    report = ''
    if request.method == 'GET':
        report = find()
    elif request.method == 'POST':
        if request.form['action'] == 'Find':
            report = find(request.form['name'])
            save_global_settings()
            mme.build_map(filter_level, settings['search']['results'])
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
    img=mme.build_map(filter_level, settings['search']['results'])
    return jsonify(img=img)


if __name__ == '__main__':
    # app.run(host='0.0.0.0', debug=True, port='5000')
    webbrowser.open('http://127.0.0.1:8080')
    serve(app, host="0.0.0.0", port=8080)
