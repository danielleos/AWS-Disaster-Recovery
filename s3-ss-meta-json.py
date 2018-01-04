# Import Statements
import boto3
import botocore
import yaml
import ruamel_yaml as ryaml
from ruamel_yaml.util import load_yaml_guess_indent as lygi
from itertools import izip
from datetime import datetime
from dateutil import parser
from dateutil.parser import parse

# Read the AMIs that exist using describe-images(**kwargs)
# Filter using specific tag-values
try:
    print "Trying to read the AMIs..."
    images = ec2.describe_images(
       Filters=[
           {
                'Name': 'owner-id',
                'Values': ['00000000000'],
                'Name': 'tag-key',
                'Values': ['Name'],
                'Name': 'tag-value',
                'Values': ['name-of-the-ec2-instance']
            },
        ],
    )
    print "Success"
except botocore.exceptions.ClientError as e:
    # If a client error is thrown, then check that it was a 404 error.
    # If it was a 404 error, then the bucket does not exist.
    error_code = int(e.response['Error']['Code'])
    print e.response['Error']
    success = False
    if error_code == 404:
        exists = False
        print e.response['Error']
#print images

# Find the AMIs (IDs) with most recent creation date
# Create a temporary lists
names = []
image_ids = []
creation_dates = []
# For every entry in the list images
for image in range(len(images['Images'])):
    names.append(images['Images'][image]['Name'])
    image_ids.append(images['Images'][image]['ImageId'])
    creation_dates.append(images['Images'][image]['CreationDate'])
    print names, image_ids, creation_dates
	
# Transform date strings into datetime objects
# NOT FINALISED
parser.parserinfo(yearfirst=True, dayfirst=False)
now = datetime.now()
#print now
dates = []
for name in names:
    for i in range(len(creation_dates)):
        dates.append(parse(creation_dates[i], fuzzy=True))
        #print dates[i]
    
recent = max(dates)
index = dates.index(recent)

# Put those AMI IDs into main_prod.yml file
# Code omitted
