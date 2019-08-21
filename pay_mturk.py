import os, csv, sys, boto3, math

HIT_IDS = [
	    "3MXX6RQ9EVK2J7YNCDA7C45UE8Y4PK",
	    "3PGQRAZX02ZFU6SZT128NYECWS3YSC",
	    "3GONHBMNHVDC11PZ5Q85PWO8AX7MZX",
	    "3ZZAYRN1I664FS1CCEY0VCCWK10OTY",
          ]

MAX_ASSIGNMENTS_PER_HIT = 300

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

region = 'us-east-1'

client = boto3.client(
    'mturk',
    region_name=region,
)

print(client.get_account_balance()['AvailableBalance'])

assignments = []
for hit_id in HIT_IDS:
    response = client.list_assignments_for_hit(HITId=hit_id)
    if 'NextToken' in response:
        print('next token')
        is_next_token = True
        next_token = response['NextToken']
        while is_next_token:
            response = client.list_assignments_for_hit(HITId=hit_id, NextToken=next_token)
            assignments.extend(response['Assignments'])
            print(f'found assignments for hit {hit_id}')
            if 'NextToken' in response:
                print('next token')
                next_token = response['NextToken']
            else:
                is_next_token = False
    else:
        print(f'found assignments for hit {hit_id}')
        assignments.extend(response['Assignments'])
print(len(assignments))

workers = []
bonus_workers = []
for assignment in assignments:
    assignment_id = assignment['AssignmentId']
    worker_id = assignment['WorkerId']
	
    answer = assignment['Answer']
    code = answer.split('<Answer><QuestionIdentifier>code</QuestionIdentifier><FreeText>')[-1].split('</FreeText></Answer><Answer><QuestionIdentifier>feedback for us</QuestionIdentifier>')[0]
    print(f'code is {code}')
    worker = {"worker_id": worker_id, "assignment_id": assignment_id, "code": code}
    if code[:2] == "SH":
        bonus_workers.append(worker)
    workers.append(worker)

print("Total number of workers: {}".format(len(workers)))
print("Total number of bonus workers: {}".format(len(bonus_workers)))
print(bonus_workers)

message = "Thanks so much for participating!"

bonus = 2

# Bonus workers
for worker in bonus_workers:
    print(worker["worker_id"])
    client.send_bonus(WorkerId=worker["worker_id"], BonusAmount=str(bonus), AssignmentId=worker["assignment_id"], Reason=message)
    print("Granted bonus to worker {}".format(worker))

print(client.get_account_balance()['AvailableBalance'])
