import yaml
from itertools import izip

# Load original environment file
with open('main_prod.yml') as stream:
    main_prod = yaml.safe_load(stream)

# Load new ImageIds file
with open('new_params.yml') as stream2:
    new_params = yaml.safe_load(stream2)

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

# Lists all roles that need updating (which should be all entries)
newIds = findImageId(new_params)

# Convert lists to dictionaries
i = iter(newIds)
newIds = dict(izip(i,i))

j = iter(originalIds)
# Change name to 'mergedIds' for comprehension
mergedIds = dict(izip(j,j))

# Change the AMI IDs for those that need updating
# For every key in the mergedIds dictionary
for i in mergedIds:
    # For every key in the newIds dictionary
    for j in newIds:
        # If these keys match up
        if i == j:
            # Then update the ID
            mergedIds[i] = newIds[j]

# Update new ImageIds and write to updated file
import ruamel.yaml as ryaml
from ruamel.yaml.util import load_yaml_guess_indent as lygi

# Set data and indentation parameters for orignal YAML file
config, ind, bsi = lygi(open('main_prod.yml'))

# Variable name for data inside the 'RoleParams' key (i.e. ignoring 'BaseParams')
RoleParams = config['RoleParams']


# Function to update AMI IDs
# Function parameter is a dictionary with the updated AMI IDs
def updateImageId(mergedIds):
    # For every role
    for i in RoleParams:
        # Find the roles that need updating
        for key in mergedIds:
            if key == i:
                # Update the ImageId
                RoleParams[i]['ImageId'] = mergedIds[key]
# Run function
updateImageId(mergedIds)


# Write to new YAML file
ryaml.round_trip_dump(config, open('output.yml', 'w'), indent=ind, block_seq_indent=bsi)
