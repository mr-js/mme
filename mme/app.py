from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from markupsafe import Markup, escape
from secrets import token_hex
from waitress import serve
import webbrowser
import pathlib
import json
import codecs
import os
from calculation import MME


app = Flask(__name__)
app.secret_key = token_hex(16)
mme = MME()
settings = dict()


def load_global_settings():
    global settings
    if os.path.isfile('settings.json'):
        with codecs.open('settings.json', 'r', 'utf-8') as f:
            settings = json.load(f)
    if 'ui' not in settings:
        settings['ui'] = {'language': mme.profile}
    else:
        mme.profile = settings['ui'].get('language', 'eng')
    if 'view_point' not in settings:
        settings['view_point'] = {'x' : 0, 'y' : 0, 'z' : 4, 's': 100}
    mme.filter_level = settings['view_point']['z']



def save_global_settings():
    global settings
    with codecs.open('settings.json', 'w', 'utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)


def __next_language():
    settings['ui']['language'] = 'ru' if settings['ui']['language'] == 'eng' else 'eng'
    return settings['ui']['language']


@app.route('/', methods=['POST', 'GET'])
def page_main():
    global mme
    load_global_settings()
    mme.build_map()
    save_global_settings()
    report = ''
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        save_global_settings()
        if request.form['action'] == 'Language':
            print(__next_language())
            save_global_settings()
            load_global_settings()
            mme.build_map()
        elif request.form['action'] == 'Patch':
            report = mme.patch_data()
            mme.build_map()
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
    name, x, y, s, status, comment, description = mme.get_point_info(name)

    return jsonify(name=name, status=status, comment=comment, description=description)


@app.get('/map_moved')
def map_moved():
    global settings
    settings['view_point'] = {
        'x': int(request.args.get('x')),
        'y': int(request.args.get('y')),
        'z': settings['view_point']['z'],
        's': int(request.args.get('s')),
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
    img = mme.build_map()
    return jsonify(img=img)


@app.get('/search_clicked')
def search_clicked():
    global mme
    report = 'Search results:\n'
    text = request.args.get('text')
    results = mme.find_points_by_text(text)
    img = mme.build_map(results)
    report += '\n'.join(f'{k}\t[{v.get("x")}:{v.get("y")}]' for k, v in results.items())
    return jsonify(img=img, text=text, report=report)


@app.get('/lod_change')
def lod_change():
    global mme
    settings['view_point']['z'] = int(request.args.get('lod'))
    save_global_settings()
    # load_global_settings()
    mme.filter_level = settings['view_point']['z']
    img = mme.build_map()
    return jsonify(img=img)

if __name__ == '__main__':
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open('http://127.0.0.1:5000')
    app.run(host='0.0.0.0', debug=True, port='5000')
    # webbrowser.open('http://127.0.0.1:8080')
    # serve(app, host="0.0.0.0", port=8080)
