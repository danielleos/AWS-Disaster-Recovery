import json
from itertools import izip

# Load local file
with open('main_prod.yml') as stream:
    main_prod = yaml.safe_load(stream)

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

j = iter(originalIds)
# Change name to 'mergedIds' for comprehension
originalIds = dict(izip(j,j))
