# Import Statements
import boto3
import botocore
import yaml
import ruamel_yaml as ryaml
from itertools import izip
import datetime
from dateutil import parser
from dateutil.parser import parse

def handler(event, context):
    success = False
    ec2 = boto3.client('ec2')
    s3 = boto3.resource('s3')
    exists = True

    # Read the AMIs that exist using describe-images(**kwargs)
    # Filter using specific tag-values
    try:
        print "Trying to read the AMIs..."
        images = ec2.describe_images(
            Filters=[
                {
                    'Name': 'owner-id',
                    'Values': ['your-account-id'],
                    'Name': 'tag-key',
                    'Values': ['Name'],
                    'Name': 'tag-value',
                    # List all the tag-values or filter based on specific image
                    # Here all the possible values are listed
                    # For future -> want to grab all possible names automatically rather than hard code these values...
                    'Values': ['name1','name2', 'name3']
                },
            ],
        )
        success = True
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
    component_names = []
    instance_names = []
    image_ids = []
    creation_dates = []
    # For every entry in the list images
    for image in range(len(images['Images'])):
        component_names.append(images['Images'][image]['Tags'][0]['Value'])
        instance_names.append(images['Images'][image]['Name'])
        image_ids.append(images['Images'][image]['ImageId'])
        creation_dates.append(images['Images'][image]['CreationDate'])

    print "Component Names: "
    print component_names
    print ""
    print "Instance Names: "
    print instance_names
    print ""
    print "Image IDs: "
    print image_ids
    print ""
    print "Creation Dates: "
    print creation_dates
    print ""
    
    # Transform date strings into datetime objects
    parser.parserinfo(yearfirst=True, dayfirst=False)
    # Create new list of dates with format updated
    dates = []
    for i in range(len(creation_dates)):
        dates.append(parse(creation_dates[i], fuzzy=True))

    print "New Formatted Creation Dates: "
    print dates
    print "\n\n"
    
    # Due to issue of pandas library not being compatible with AWS
    # Have to create 3 separate dictionaries to associate the values together
    names_dates = {}
    dates_ids = {}
    ids_names = {}
    for i in range(0,len(instance_names)):
        names_dates[instance_names[i]] = dates[i]
        dates_ids[dates[i]] = image_ids[i]
        ids_names[image_ids[i]] = component_names[i]

    # Make list of Component Names distinct
    component_names = list(set(component_names))
    
    print "==========Names & Dates=========="
    print names_dates
    print ""
    print "==========Dates & IDs=========="
    print dates_ids
    print ""
    print "==========IDs & Names=========="
    print ids_names
    print ""
    print "==========Component Names=========="
    print component_names
    print ""
    print "==========Instance Names=========="
    print instance_names
    print "\n\n"

    # Find most recent date and associated instance name
    # Create dictionary for component names and recent dates
    temp_output = {}
    # For every entry inside the component_names list
    for cname in component_names:
        flag = True
        instance_dates = []
        recent = datetime.datetime.now()
        print "==========Component Name is: " + cname
        print "The time now is: " + str(recent)
        # Look at every entry inside the names & dates dictionary
        for iname in names_dates:
            loop = False
            print "Instance Name is: " + iname
            # Check if the name from the dictionary starts with the name in the component name list
            if iname.startswith(cname[:-3]):
                print "There is a majority match of name"
                # Add date to list
                instance_dates.append(names_dates[iname])
                # Then find the max out of those
                recent = max(instance_dates)
                print "\nMost Recent Time for " + cname + " is: " + str(recent) + "\n"
                # Put in a dictionary with the component name as the key and most recent creation date as the value
                temp_output[cname] = recent
                continue
            # Else move onto the next cname
            if not flag:
                break

    print "\n==========OUTPUT========="
    print temp_output
    print ""

    # Associate Image IDs with relevant times
    # Create new dictionary
    find_images = {}
    for value in temp_output:
        # New dictionary has keys as component name and values as AMI IDs
        find_images[value] = dates_ids[temp_output[value]]
    print "Find the image ids for associated recent times..."
    print find_images
    print ""
	
	# Optional: match the names according to convention

    # Change output into dictionary format with RoleParams
    final = {}
    final['RoleParams'] = output
    print final
    print ""
    
    # Put those AMI IDs into new_prod.yml file
    with open('/tmp/test-new-params.yml', 'w') as outfile:
        yaml.safe_dump(final, outfile, default_flow_style=False)
    # Upload to S3 bucket
    # Putting data into a file in S3
    exists = True
    try:
        s3.meta.client.upload_file('/tmp/test-new-params.yml', 'name-of-s3-bucket',
                                   'new_params.yml')
        print "Uploaded the file to S3 bucket!"
        success = True
    except botocore.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = int(e.response['Error']['Code'])
        print e.response['Error']
        success = False
        if error_code == 404:
            exists = False
            print e.response['Error']
    
    return success
