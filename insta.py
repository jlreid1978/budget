import json
import os
import zipfile


def extract_zip(file_path, extract_to):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def parse_followers(directory):
    follow = []
    followers_path = os.path.join(directory, 'connections', 'followers_and_following')
    for filename in os.listdir(followers_path):
        if filename.startswith('followers') and filename.endswith('.json'):
            with open(os.path.join(followers_path, filename), 'r') as f:
                data = json.load(f)
                for item in data:
                    idata = item.get('string_list_data')
                    for d in idata:
                        follow.append(d.get('value'))
    return follow

def parse_following(directory):
    following_path = os.path.join(directory, 'connections', 'followers_and_following', 'following.json')
    following = []
    if not os.path.exists(following_path):
        return None  # Return None if the file does not exist
    with open(following_path, 'r') as f:
        data = json.load(f)
        for item in data.get('relationships_following', []):
            idata = item.get('string_list_data')
            for d in idata:
                following.append(d.get('value'))
    return following