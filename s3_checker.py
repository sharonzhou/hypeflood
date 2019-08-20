import json

with open('app/static/s3_data.json') as f:
    data = json.load(f)
    img_urls = data['img_urls']
    worker_urls = data['worker_urls']
    tutorial_img_urls = data['tutorial_img_urls']

for i in range(100):
    if str(i) not in worker_urls.keys():
        print(f'{i} not in worker keys!')

for v in worker_urls.values():
    if len(v) < 50:
        print(f'{v} is too short')
 

