# Generate a markdown webportal from your public repos 

# Imports
from urllib import request, error
from json import loads
from os import path, mkdir, makedirs
from bs4 import BeautifulSoup

# Constants
output_dir = "output/"
last_usage = path.join(output_dir, "data.txt")
assets_dir = path.join(output_dir, "assets/")

# Functions
def get(url):
    req = request.urlopen(url)
    res = req.read()
    req.close()
    return res

def save_image(url, filename):
    request.urlretrieve(url, path.join(assets_dir, filename))


# ----- MAIN -----
# Create output & asset dir
makedirs(assets_dir, exist_ok=True)

# If this script was run before, suggest the previous username or osoc
try:
    with open(last_usage, "r") as file:
        old_user_or_org = file.read()
except FileNotFoundError:
    old_user_or_org = ""

# Prompt oser for user or organisation name, create api URL
user_or_org = input("Insert username or organisation name [{0}]: ".format(old_user_or_org)) or old_user_or_org
if old_user_or_org is not user_or_org:
    with open(last_usage, "w") as file:
        file.writelines(user_or_org)

url = "https://api.github.com/users/{0}/repos".format(user_or_org)

# Get the data using Githubs API, parse JSON

data = loads(get(url))


header_img = data[0]["owner"]["avatar_url"]
save_image(header_img, "user_or_org.png")

repos = list()
for raw_repo in data:
    """
    readme code meant to get img from README, but actually that wouldn't include markdown notation so honestly not good idea

    readme_url = "https://raw.githubusercontent.com/{0}/{1}/README.md".format(raw_repo["full_name"], raw_repo["default_branch"])
    try:
        readme = get(readme_url)
        print(BeautifulSoup(readme).find("img"))


    except error.HTTPError:
        pass
    """
    

    # Save data used in output
    repo = {
        "name": raw_repo["name"],
        "repo-url": raw_repo["html_url"],
        "website-url": raw_repo["homepage"],
        
    }
    
    repos.append(repo)

print(repos)
