# Import statements
# Make sure these package names match the folder names in the zip file to upload to AWS Lambda
import yaml
from itertools import izip
import boto3
import botocore
import ruamel_yaml as ryaml
from ruamel_yaml.util import load_yaml_guess_indent as lygi

# Handler function that AWS Lambda calls
def handler(event, context):
    s3 = boto3.resource('s3')
    exists = True
    success = False

    try:
        print "Trying to download this file..."
        s3.Bucket('name-of-s3-bucket').download_file(
            'main_prod.yml', '/tmp/main_prod.yml')
        # S3 buckets can be the same or different - depends on the paths of the relevant files
        s3.Bucket('name-of-s3-bucket').download_file(
            'new_params.yml', '/tmp/new_params.yml')
        print "Success"
    except botocore.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = int(e.response['Error']['Code'])
        print e.response['Error']
        if error_code == 404:
            exists = False
            print e.response['Error']

    # Load file from local source
    with open('/tmp/main_prod.yml') as stream:
        main_prod = yaml.safe_load(stream)
    print "Opened local /tmp/main_prod.yml file"
    # Load new ImageIds file
    with open('/tmp/new_params.yml') as stream2:
        new_params = yaml.safe_load(stream2)
    print "Opened local /tmp/new_params.yml file"

    # Function for finding the 'ImageId' in nested dictionary
    def findImageId(d):
        # Create empty list
        temp = []
        # For every role
        for i in d['RoleParams']:
            # Find the 'ImageId' property
            if 'ImageId' in d['RoleParams'][i]:
                # Output both the role name and the value of the 'ImageId' associated with it
                temp.append(i)
                temp.append(d['RoleParams'][i]['ImageId'])
        return temp

    # Lists all roles and associated AMI IDs
    originalIds = findImageId(main_prod)
    print "Found the Image Ids for main_prod"
    # Lists all roles that need updating (which should be all entries)
    newIds = findImageId(new_params)
    print "Found the Image Ids for new_params"

    # Convert lists to dictionaries
    i = iter(newIds)
    newIds = dict(izip(i,i))
    print "Made the new_params list into a dict"

    j = iter(originalIds)
    # Change name to 'updatedIds' for comprehension
    updatedIds = dict(izip(j,j))
    print "Made the oroginal list into a new dict ready for updating"

    # Change the AMI IDs for those that need updating
    # For every key in the mergedIds dictionary
    for i in updatedIds:
    # For every key in the newIds dictionary
        for j in newIds:
            # If these keys match up
            if i == j:
                # Then update the ID
                updatedIds[i] = newIds[j]

    print "IDs successfully updated"

    # Update new ImageIds and write to updated file
    # Set data and indentation parameters for orignal YAML file
    config, ind, bsi = lygi(open('/tmp/main_prod.yml'))
    print "Setting indentation ready for updating YAML file..."

    # Variable name for data inside the 'RoleParams' key (i.e. ignoring 'BaseParams')
    RoleParams = config['RoleParams']
    print "Let's ignore the BaseParams section to update"

    # For every role, update the ImageIds
    for i in RoleParams:
        # Find the roles that need updating
        for key in updatedIds:
            if key == i:
                # Update the ImageId
                RoleParams[i]['ImageId'] = updatedIds[key]

    print "We have updated the IDs whilst keeping the YAML structure intact"

    # Write to new YAML file
    ryaml.round_trip_dump(config, open('/tmp/main_prod.yml', 'w'), indent=ind, block_seq_indent=bsi)
    print "Saved the new YAML file locally as /tmp/main_prod.yml"

    # Putting data into a file in S3
    exists2 = True
    try:
        s3.meta.client.upload_file('/tmp/main_prod.yml', 'name-of-s3-bucket',
                                   'output.yml')
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
