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

# TODO: S3 bucket scrape - get num images total (HYPE general) and maybe hard code hype flood with num images in each?
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
    # TODO: replace triplets per task -> tutorial + img_per_task (do this first, and just log out bad ppl early)
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

    # Return initial image
    img = np.random.choice(num_images)

    # TODO: S3 bucket base url
    ffhq_dir = '/static/img/ffhq_images/ffhqrealtwo/'
    img_filepath = ffhq_dir + id2img[str(img)]

    image = {}
    image['img'] = img
    image['img_filepath'] = img_filepath
    # TODO: return an encrypted filepath name?
    print(image)
    return render_template("task.html", image=image)

@app.route("/feedback", methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        data = json.loads(request.get_data())
        print(data)
        selection = Selection(
                    img_id=data['img'],
                    selected=data['selected'],
                    uid=session['uid']
                    )

        print(selection)

        db.session.add(selection)
        db.session.commit()
        
        if 'counter' not in session:
            session['counter'] = 0
        session['counter'] += 1
        print('counter is', session['counter'])
        
        next_data = {}
        
        # TODO: Compute correctness with obfuscated URLs
        if 'real' in data['img']:
            correctness = data['selected'] == 'real'
        else:
            correctness = data['selected'] == 'fake'

        next_data["img"] = np.random.choice(num_images)
        next_data["counter"] = session["counter"]
        next_data["correctness"] = correctness
        
        print('next data', next_data)
        return json.dumps({"data": next_data, "success": True})
    else:
        print('get request')
        return None

