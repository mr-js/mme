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
app.config['DEBUG'] = True
app.secret_key = token_hex(16)
mme = MME()


def load_global_settings():
    settings = dict()
    if os.path.isfile('settings.json'):
        try:
            with codecs.open('settings.json', 'r', 'utf-8') as f:
                settings = json.load(f)
        except:
            pass
    session['language'] = settings.get('language', 'eng')
    mme.profile = session['language']
    session['view_point'] = settings.get('view_point', {'x' : 0, 'y' : 0, 'z' : 4, 's': 100})
    mme.filter_level = session['view_point']['z']


def save_global_settings():
    global settings
    with codecs.open('settings.json', 'w', 'utf-8') as f:
        json.dump(session, f, ensure_ascii=False, indent=4)


@app.route('/', methods=['POST', 'GET'])
def page_main():
    global mme
    load_global_settings()
    mme.build_map()
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        pass
    # save_global_settings()
    names = mme.find_points_by_text('')
    report = 'Ready'
    return render_template('main.html', img=mme.img, names=names, report=report)


@app.get('/map_init')
def map_init():
    return jsonify(view_point=session['view_point'])


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
    session['view_point'] = {
        'x': int(request.args.get('x')),
        'y': int(request.args.get('y')),
        'z': session['view_point']['z'],
        's': int(request.args.get('s')),
    }
    save_global_settings()

    return jsonify(comment=session['view_point'])


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
    text = request.args.get('text')
    results = mme.find_points_by_text(text)
    report = f'Found: {len(results)}'
    img = mme.build_map(results)
    return jsonify(img=img, text=text, report=report)


@app.get('/lod_change')
def lod_change():
    global mme
    session['view_point']['z'] = int(request.args.get('lod'))
    mme.filter_level = session['view_point']['z']
    save_global_settings()
    load_global_settings()
    img = mme.build_map()
    return jsonify(img=img)


@app.get('/change_language')
def change_language():
    session['language'] = 'ru' if session['language'] == 'eng' else 'eng'
    mme.filter_level = session['view_point']['z']
    save_global_settings()
    load_global_settings()
    mme.build_map()
    # load_global_settings()
    return redirect(url_for('page_main'))


@app.get('/run_patch')
def run_patch():
    save_global_settings()
    report = mme.patch_data()
    # report += '\n'.join(f'{k}\t[{v.get("x")}:{v.get("y")}]' for k, v in results.items())
    mme.build_map()
    load_global_settings()
    return jsonify(report=report)


if __name__ == '__main__':
    if app.debug:
        if not os.environ.get("WERKZEUG_RUN_MAIN"):
            webbrowser.open('http://127.0.0.1:5000')
        app.run(host='0.0.0.0', debug=True, port='5000')
    else:
        webbrowser.open('http://127.0.0.1:8080')
        serve(app, host="0.0.0.0", port=8080)
