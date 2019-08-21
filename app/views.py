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
import hashlib


# Local images
with open('app/static/s3_data.json') as f:
    data = json.load(f)
    img_urls = data['img_urls']
    worker_urls = data['worker_urls']
    tutorial_img_urls = data['tutorial_img_urls']
 
# Local constants
with open('app/static/constants.json') as f:
    data = json.load(f)
    num_tutorial = data['num_tutorial']
    num_per_task = data['num_per_task']
    num_images = data['num_images']
    tutorial_pass_acc = data['tutorial_pass_acc']


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

        # Check if worker already did task
        check_worker_exists = Worker.query.filter(Worker.amt_id == amt_id).first()
        if check_worker_exists is not None:
            print(f'Repeat worker {check_worker_exists}')
            
            # Save AMT id for checking in finish()
            session['amt_id'] = amt_id

            next_data = { 'url_': '/finish' }
            return json.dumps({"data": next_data, "success": True})
            
        
        # Sasha only: assign data dir id
        # Get all unassigned data_dir_ids
        unassigned_data_dir_ids = DataDir.query.filter(DataDir.status == "unassigned").all()

        # If at least one exists, the select a random one
        if len(unassigned_data_dir_ids) > 0:
            data_dir = random.choice(unassigned_data_dir_ids)
            data_dir_id = data_dir.id
            data_dir.status = "softassigned"
            db.session.commit()
        else:
            # Look for soft assigned ones (means worker still going through tutorial) and randomly select one
            soft_assigned_data_dir_ids = DataDir.query.filter(DataDir.status == "softassigned").all()
            if len(soft_assigned_data_dir_ids) > 0:
                data_dir = random.choice(soft_assigned_data_dir_ids)
                data_dir_id = data_dir.id
            else:
                # Look for assigned ones and randomly select one
                assigned_data_dir_ids = DataDir.query.filter(DataDir.status == "assigned").all() 
                if len(assigned_data_dir_ids) > 0:
                    data_dir = random.choice(assigned_data_dir_ids)
                    data_dir_id = data_dir.id
                else:
                    # Else, everything is done... so redirect to page saying task is over
                    next_data = { 'url_': '/hitover' }
                    return json.dumps({"data": next_data, "success": True})
        
        uid = Worker(amt_id=amt_id,
                     data_dir_id=data_dir_id)

        db.session.add(uid)
        db.session.commit()

        session['uid'] = uid.id
        session['amt_id'] = amt_id

        session['data_dir_id'] = data_dir_id
        session['data_dir_name'] = str(data_dir.name)

        session['counter'] = 0

        print('session is', session)

        next_data = { 'url_': '/task' }
        return json.dumps({"data": next_data, "success": True})


@app.route("/finish", methods=['GET', 'POST'])
def finish():
    # End and give completion code
    if 'counter' in session and session['counter'] >= num_per_task:
        # partial_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
        hash_string = str(session['amt_id']) + 'donethanks'
        hashed_code = hashlib.sha1(hash_string.encode('utf-8')).hexdigest()[:10].upper()
        completion_code = "SH" + hashed_code + "DEZ"
        
        # Update worker in db - complete
        worker = Worker.query.get(session['uid'])
        worker.is_finished = True
        worker.completion_code = completion_code
        db.session.commit()

        # Update data dir in db - complete
        data_dir_id = session['data_dir_id']
        data_dir = DataDir.query.get(data_dir_id)
        data_dir.status = "complete"
        db.session.commit()
        
        print(f'user {session} successfully finishes with completion code {completion_code}')
        
        return render_template("finish.html", completion_code=completion_code)
    
    # Did not pass tutorial
    elif ('spammer' in session and session['spammer'] is True) or (('counter' in session) and (session['counter'] == num_tutorial) and (session['num_correct'] / float(session['counter']) < tutorial_pass_acc)):

        # (in)completion code for incomplete task
        hash_string = str(session['amt_id']) + 'epicfail'
        hashed_code = hashlib.sha1(hash_string.encode('utf-8')).hexdigest()[:10].upper()
        completion_code = "EDZ" + hashed_code + "HS"
        
        # Update worker in db - not passed tutorial
        worker = Worker.query.get(session['uid'])
        worker.passed_tutorial = 0
        worker.completion_code = completion_code
        db.session.commit()

        # Update data dir in db - unassigned
        data_dir_id = session['data_dir_id']
        data_dir = DataDir.query.get(data_dir_id)
        # TODO: For cleaner method, technically should check if another user is working on this and has it softassigned to them
        if data_dir.status == "softassigned":
            data_dir.status = "unassigned"
            db.session.commit()
        
        print(f'spammer {session} finishes with completion code {completion_code}')

        return render_template("sorry.html", completion_code=completion_code)
    
    # Trying to access this page, redirecting to home unless repeat worker
    else:
        # Check if worker already exists
        if 'amt_id' in session:
            amt_id = session['amt_id']
            check_worker_exists = Worker.query.filter(Worker.amt_id == amt_id).first()
            if check_worker_exists is not None:
                completion_code = check_worker_exists.completion_code
                if completion_code[:2] == "SH":
                    print(f'user {session} revisits finish page with completion code {completion_code}')
                    return render_template("finish.html", completion_code=completion_code)
                elif completion_code[:3] == "EDZ":
                    print(f'spammer {session} revisits finish page with completion code {completion_code}')
                    return render_template("sorry.html", completion_code=completion_code)
                elif completion_code == "incomplete":
                    print(f'repeat incomplete completion code user {session}')
                    return render_template("repeat.html")

        return render_template("index.html")


@app.route("/idle", methods=['GET', 'POST'])
def idle():
    # Active user no longer exists
    if 'uid' not in session:
        return render_template("index.html")

    # Update user in db to have passed_tutorial = 0
    worker = Worker.query.get(session['uid'])
    worker.passed_tutorial = 0
    db.session.commit()

    print(f'user {session} idle and dropped out')

    # Redirect to home
    return render_template("index.html")


@app.route("/task", methods=['GET', 'POST'])
def start():
    # Active user no longer exists
    if 'uid' not in session:
        return render_template("index.html")

    uid = session['uid'] 
    print('uid is', uid)

    # Return initial image
    #img = np.random.choice(num_images)
    
    data_dir_id = session['data_dir_id']
    data_dir_name = session['data_dir_name']

    tutorial_url_idx = 0
    img_filepath = worker_urls['spammers'][tutorial_url_idx]

    image = {}
    image['bg-div'] = img_filepath
    image['img'] = img_filepath

    print(f'uid {uid} starts with {data_dir_id} data dir, name {data_dir_name}')
    return render_template("task.html", image=image)

@app.route("/feedback", methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        data = json.loads(request.get_data())
        print(data)
        
        img_src = data['bg-div']
        img_name = img_src.split('/')[-1]
        
        # Sasha only, where naming of files correspond to fake/real
        if ('fake' in data['bg-div']) or ('output' in data['bg-div']):
            correctness = data['selected'] == 'fake'
        else:
            correctness = data['selected'] == 'real'
        
        selection = Selection(
                    img_name=img_name,
                    img_src=img_src,
                    selected=data['selected'],
                    correctness=correctness,
                    uid=session['uid']
                    )

        print(selection)

        db.session.add(selection)
        db.session.commit()
        
        if 'counter' not in session:
            session['counter'] = 0
        session['counter'] += 1
        print('counter is', session['counter'], 'for uid', session['uid'])
        counter = session['counter']

        # Increment num correct counter
        if 'num_correct' not in session:
            session['num_correct'] = 0.
        if correctness:
            session['num_correct'] += 1
        frac_correct = round(session["num_correct"] / float(counter), 2)

        next_data = {}
        #next_data["bg-div"] = np.random.choice(num_images)
        
        # Check if completed task
        if counter >= num_per_task:
            next_data['is_finished'] = True
            session['is_finished'] = True

            print('uid', session['uid'], 'completed!')

            return json.dumps({"data": next_data, "success": True})

        # Check if gone through tutorial or on to worker's own task
        elif counter >= num_tutorial:
            
            # Check if passed tutorial
            if counter == num_tutorial and frac_correct < tutorial_pass_acc:

                # Log out and give completion code with certain money amount
                next_data['is_finished'] = True
                session['spammer'] = True

                print('uid', session['uid'], 'spammer detected. next data', next_data)

                return json.dumps({"data": next_data, "success": True})
            
            else:
                # Else, continue

                if counter == num_tutorial:
                    # Update worker in db - passed tutorial
                    worker = Worker.query.get(session['uid'])
                    worker.passed_tutorial = 1
                    db.session.commit()

                    session['spammer'] = False

                    # Update data dir in db - assigned
                    data_dir = DataDir.query.get(session['data_dir_id'])
                    # Only if someone else has not completed it 
                    # TODO: If someone else has completed it, assigned a different data_dir_id
                    if data_dir.status != "complete":
                        data_dir.status = "assigned"
                        db.session.commit()

                    print('uid', session['uid'], 'passed tutorial!')

                worker_url_idx = counter - num_tutorial
               
                data_dir_id = session['data_dir_id']
                data_dir_name = session['data_dir_name']
                
                next_data["bg-div"] = worker_urls[data_dir_name][worker_url_idx]
                next_data['spammer'] = False
                print('[task] next data', next_data, 'for uid', session['uid'])
        else:
            # Still in tutorial
            tutorial_url_idx = counter
            next_data["bg-div"] = worker_urls['spammers'][tutorial_url_idx]
            next_data['spammer'] = False
            print('[tutorial] next data', next_data, 'for uid', session['uid'])

        next_data["counter"] = counter
        next_data["frac_correct"] = str(frac_correct)
        next_data["correctness"] = correctness
        
        print('next data', next_data)
        return json.dumps({"data": next_data, "success": True})
    else:
        print('get request')
        return None

@app.route("/hitover")
def hitover():
    print('hit is over!')
    return render_template("hitover.html")

# S3 preprocess step/endpoint
@app.route('/files')
def get_files():
    # Sasha only -> move to constants
    S3_BUCKET = 'hypeaug2019'
    S3_BUCKET_SUBDIR = 'Hype_120_v2' # Hype_120

    # This is a backup suffix for file to avoid override of production s3 data json file
    OUTFILE_SUFFIX = 'v2' # v1
    
    outfile_path = Path(f'app/static/s3_data.json')
    if outfile_path.exists():
        outfile_path = Path(f'app/static/s3_data_{OUTFILE_SUFFIX}.json')
        print(f'Saving to backup file {outfile_path}. Make sure to cp to s3_data.json for production.')

    s3 = boto3.resource('s3')
    s3.meta.client.meta.events.register('choose-signer.s3.*', disable_signing)
    my_bucket = s3.Bucket(S3_BUCKET)
    summaries = my_bucket.objects.all()
    
    base_url = 'https://' + S3_BUCKET + '.s3.amazonaws.com/'
    all_img_urls = []
    tutorial_img_urls = []
    worker_urls = {}
    for obj in summaries:
        if S3_BUCKET_SUBDIR not in obj.key:
            continue
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
    print(worker_urls['spammers'])
    for data_dir_id, img_urls in worker_urls.items():
        np.random.shuffle(img_urls)
        shuffled_worker_urls[data_dir_id] = img_urls
    worker_urls = shuffled_worker_urls
    print(worker_urls['spammers'])

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
    with open(f'', 'w') as f:
        j = json.dumps(s3_data)
        f.write(j)

    return render_template('files.html', s3_data=s3_data)
