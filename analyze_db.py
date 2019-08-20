import os
import operator
from urllib import parse
import psycopg2
import psycopg2.extras
import numpy as np
from collections import defaultdict
from datetime import datetime

parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

cursor = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

query = "select * from selection;"
cursor.execute(query)
selections = cursor.fetchall()

query = "select * from worker;"
cursor.execute(query)
workers = cursor.fetchall()

query = "select * from data_dir;"
cursor.execute(query)
data_dirs = cursor.fetchall()


# Get valid workers
# id > 70, completion code starting with SH
wcols2id = { 'id': 0,
            'amt_id': 1,
            'data_dir_id': 2,
            'passed_tutorial': 3,
            'is_finished': 4,
            'completion_code': 5,
          }

valid_workers = [ (w[wcols2id['id']], w[wcols2id['data_dir_id']]) for w in workers if w[wcols2id['completion_code']][:2] == "SH" ]
valid_worker_ids = [ vw[0] for vw in valid_workers ]
print('valid workers (uid, data_dir_id)', valid_workers, len(valid_workers))

# Filter selections by valid workers based on uid
scols2id = { 'id': 0,
             'timestamp': 1,
             'img_name': 2,
             'img_src': 3,
             'selected': 4,
             'correctness': 5,
             'uid': 6,
           }

valid_selections = [ (s[scols2id['img_name']], s[scols2id['selected']], s[scols2id['correctness']], s[scols2id['uid']]) for s in selections if s[scols2id['uid']] in valid_worker_ids ]
print('valid selections (img_name, selected (real/fake), correctness, uid)', len(valid_selections))

# Group selections based on real/fake
# Look specifically at *fake* images ('fake' in name -> look at 'output' later b/c many of them)
fake_selections = [ s for s in selections if 'fake' in s[scols2id['img_name']] ]
print('fake selections', len(fake_selections))

# Group by image id and style id
# img dict { image_id : [ selections ] }
# style dict { style_id : [ selections ] }
# style2img dict { style_id : { image_id : [ selections ] , ... } ... }

img_dict = defaultdict(list)
style_dict = defaultdict(list)
style2img_dict = defaultdict(lambda: defaultdict(list))
for _, _, img_name, _, selected, correctness, uid in fake_selections:
    img_name_cleaned = img_name.replace('\")', '')
    img_dict[img_name_cleaned].append(correctness)

    style_id = img_name.split('s_')[-1].split('.jpg')[0]
    style_dict[style_id].append(correctness)

    style2img_dict[style_id][img_name_cleaned].append(correctness)

# Accuracy for each image: mean, range, std dev
print('mean, std dev, min, max')
img_means = [ np.mean(c) for c in img_dict.values() ]
print('image scores for each image', img_means)

img_scores = [ s for c in img_dict.values() for s in c ]
print('image scores', np.mean(img_scores), np.std(img_scores), np.min(img_scores), np.max(img_scores))

print('ranked images by score')
img_means_dict = { i: np.mean(c) for i,c in img_dict.items() }
sorted_imgs = sorted(img_means_dict.items(), key=operator.itemgetter(1))
print(sorted_imgs)

# Accuracy for each style: mean, range, std dev
style_means = [ np.mean(c) for c in style_dict.values() ]
print('style scores for each style', style_means)

style_scores = [ s for c in style_dict.values() for s in c ]
print('style scores', np.mean(style_scores), np.std(style_scores), np.min(style_scores), np.max(style_scores))

print('ranked styles by score')
style_means_dict = { i: np.mean(c) for i,c in style_dict.items() }
sorted_styles = sorted(style_means_dict.items(), key=operator.itemgetter(1))
print(sorted_styles)



