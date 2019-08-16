from flask import render_template, url_for, redirect, request, jsonify, session
from app import app, db
from app.models import *
import json
import numpy as np
import scipy
import scipy.stats as stats
import operator
import random
import string

with open('app/static/img/images.json') as f:
    json_images = json.load(f)
    id2img = json_images['id2img']
    img2id = json_images['img2id']
    num_images = len(img2id.keys())
    with open('app/static/constants.json') as j:
        constants = json.load(j)
        print(constants)
        num_images = constants['num_images']
        triplets_per_task = constants['triplets_per_task']

@app.route("/")
def index():
    """Task home with instructions TODO
    """
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    # Initialize user session and save AMT id
    if request.method == 'POST':
        data = json.loads(request.get_data())
        print(data)
        amt_id = data['amt_id']

        uid = Worker(amt_id=amt_id)
        db.session.add(uid)
        db.session.commit()
        session['uid'] = uid.id
        print('session is', session)
        return render_template("index.html")

@app.route("/finish", methods=['GET', 'POST'])
def finish():
    # End and give completion code
    if 'counter' in session and session['counter'] > triplets_per_task:
        partial_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
        completion_code = "SH" + partial_code + "DEZ"
        return render_template("finish.html", completion_code=completion_code)
    else:
        return render_template("index.html")


@app.route("/task", methods=['GET', 'POST'])
def start():
    uid = session['uid'] 
    print('uid is', uid)

    # Return initial triplet
    root_img = np.random.choice(num_images)
    img1 = np.random.choice(num_images)
    img2 = np.random.choice(num_images)

    ffhq_dir = '/static/img/ffhq_images/ffhqrealtwo/'
    root_img_filepath = ffhq_dir + id2img[str(root_img)]
    img1_filepath = ffhq_dir + id2img[str(img1)]
    img2_filepath = ffhq_dir + id2img[str(img2)]

    images = {}
    images['root_img'] = root_img
    images['img1'] = img1
    images['img2'] = img2
    images['root_img_filepath'] = root_img_filepath
    images['img1_filepath'] = img1_filepath
    images['img2_filepath'] = img2_filepath
    return render_template("task.html", images=images)

@app.route("/compute", methods=['GET', 'POST'])
def compute():
    if request.method == 'POST':
        data = json.loads(request.get_data())
        print(data)
        triplet = Triplet(
                    root_img=data['root_img'],
                    img1=data['img1'],
                    img2=data['img2'],
                    img_selected=data['img_selected'],
                    uid=session['uid']
                    )

        print(triplet)

        db.session.add(triplet)
        db.session.commit()
        
        if 'counter' not in session:
            session['counter'] = 0
        session['counter'] += 1
        print('counter is', session['counter'])
        
        next_data = {}

        next_data["root_img"] = np.random.choice(num_images)
        next_data["img1"] = np.random.choice(num_images)
        next_data["img2"] = np.random.choice(num_images)
        while next_data["img2"] == next_data["img1"]:
            next_data["img2"] = np.random.choice(num_images)
        next_data["counter"] = session["counter"]
        
        print('next data', next_data)
        return json.dumps({"data": next_data, "success": True})
    else:
        print('get request')
        return None

