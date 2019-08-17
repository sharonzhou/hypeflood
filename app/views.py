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
import boto3
from botocore.handlers import disable_signing

# Local images
with open('app/static/s3_data.json') as f:
    data = json.load(f)
    img_urls = data['img_urls']
    worker_urls = data['worker_urls']
    tutorial_img_urls = data['tutorial_img_urls']
    
    # Sasha only -> move to constants
    num_tutorial = data['num_tutorial']
    num_per_task = data['num_per_task']
    num_images = data['num_images']

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

        # Sasha only: assign data dir id
        # Get last worker who is non-spammer, get their data_dir_id, increment by 1
        prev_worker_passed = Worker.query.filter(Worker.passed_tutorial != 0).order_by(Worker.id.desc()).first()
        if prev_worker_passed is None:
            print('First worker')
            data_dir_id = 0
        else:
            data_dir_id = prev_worker_passed.data_dir_id + 1

        uid = Worker(amt_id=amt_id,
                    data_dir_id=data_dir_id)

        db.session.add(uid)
        db.session.commit()
        session['uid'] = uid.id
        session['data_dir_id'] = data_dir_id
        print('session is', session)
        return render_template("index.html")

@app.route("/finish", methods=['GET', 'POST'])
def finish():
    # End and give completion code
    # TODO: log out bad ppl early and update passed_tutorial = 0 on their db
    if 'counter' in session and session['counter'] > num_per_task:
        partial_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
        completion_code = "SH" + partial_code + "DEZ"
        return render_template("finish.html", completion_code=completion_code)
    else:
        return render_template("index.html")


@app.route("/task", methods=['GET', 'POST'])
def start():
    uid = session['uid'] 
    print('uid is', uid)

    data_dir_id = session['data_dir_id']

    # Return initial image
    #img = np.random.choice(num_images)

    worker_imgs = worker_urls[str(data_dir_id)]
    img_filepath = worker_imgs[0] 

    image = {}
    image['bg-div'] = img_filepath
    image['img'] = 'https://hypeaug2019.s3.amazonaws.com/Hype_120/spammers/output000.jpg'

    print(image)
    return render_template("task.html", image=image)

@app.route("/feedback", methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        data = json.loads(request.get_data())
        print(data)
        
        img_src = data['bg-div']
        img_name = img_src.split('/')[-1]
        selection = Selection(
                    img_name=img_name,
                    img_src=img_src,
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

        if 'num_correct' not in session:
            session['num_correct'] = 0.
        
        next_data = {}
       
        # Sasha only, where naming of files correspond to fake/real
        if ('fake' in data['bg-div']) or ('output' in data['bg-div']):
            correctness = data['selected'] == 'fake'
        else:
            correctness = data['selected'] == 'real'
        
        # Increment num correct counter
        if correctness:
            session['num_correct'] += 1

        #next_data["bg-div"] = np.random.choice(num_images)
        data_dir_id = session['data_dir_id']

        # Check if gone through tutorial or on to worker's own task
        if session['counter'] >= num_tutorial:
            # Gone through tutorial
            # TODO: Check if passed tutorial
            # If not, log out and give completion code with certain money amount

            # Else, continue
            worker_url_idx = session['counter'] - num_tutorial
            next_data["bg-div"] = worker_urls[str(data_dir_id)][worker_url_idx]
        else:
            # Still in tutorial
            tutorial_url_idx = session['counter']
            next_data["bg-div"] = tutorial_img_urls[tutorial_url_idx]

        next_data["counter"] = session["counter"]
        next_data["frac_correct"] = str(round(session["num_correct"] / float(session["counter"]), 2))
        next_data["correctness"] = correctness
        
        print('next data', next_data)
        return json.dumps({"data": next_data, "success": True})
    else:
        print('get request')
        return None


# S3 preprocess step/endpoint
@app.route('/files')
def get_files():
    # Sasha only -> move to constants
    S3_BUCKET = 'hypeaug2019'

    s3 = boto3.resource('s3')
    s3.meta.client.meta.events.register('choose-signer.s3.*', disable_signing)
    my_bucket = s3.Bucket(S3_BUCKET)
    summaries = my_bucket.objects.all()
    
    base_url = 'https://' + S3_BUCKET + '.s3.amazonaws.com/'
    all_img_urls = []
    tutorial_img_urls = []
    worker_urls = {}
    for obj in summaries:
        img_url = base_url + obj.key
        all_img_urls.append(img_url)

        # Sasha only -> will not need this specifics for general hype
        worker_data_dir_id = obj.key.split('/')[1]
        if worker_data_dir_id not in worker_urls:
            worker_urls[worker_data_dir_id] = []
        worker_urls[worker_data_dir_id].append(img_url)
        
        # Sasha only -> prolly take first 50 in both real/ and fake/
        if 'spammers' in img_url:
            tutorial_img_urls.append(img_url)

    # Sasha only -> randomize order of each worker's set of urls
    shuffled_worker_urls = {}
    for data_dir_id, img_urls in worker_urls.items():
        np.random.shuffle(img_urls)
        shuffled_worker_urls[data_dir_id] = img_urls
    worker_urls = shuffled_worker_urls

    # Sasha only -> move to constants. In future, take from some user-specified parameter of desired CI.
    num_tutorial = len(tutorial_img_urls) # 50
    num_per_task = num_tutorial + 50
    num_images = num_per_task

    s3_data = {}
    s3_data['img_urls'] = all_img_urls
    s3_data['worker_urls'] = worker_urls
    s3_data['tutorial_img_urls'] = tutorial_img_urls

    # Sasha only -> maybe take these out of here and into constants
    s3_data['num_tutorial'] = num_tutorial
    s3_data['num_per_task'] = num_per_task
    s3_data['num_images'] = num_images

    # Storing this locally for now - should be on requester side, not this worker facing app
    # Which then creates a json file containing this object or something
    print(s3_data)
    with open('app/static/s3_data.json', 'w') as f:
        j = json.dumps(s3_data)
        f.write(j)

    return s3_data
