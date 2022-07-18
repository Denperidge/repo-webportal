# Generate a markdown webportal from your public repos 

# Imports
from urllib import request, error
from json import loads, dumps
from os import path, makedirs
from shutil import copy2

# Constants
output_dir = "output/"
last_usage = path.join(output_dir, "data.txt")
#assets_dir = path.join(output_dir, "assets/")
site_filename = path.join(output_dir, "index.md")
cache_file = path.join(output_dir + "cache.txt")


# Functions
def read_txt(name, default):
    try:
        with open(name, "r") as file:
            data = file.read()
    except FileNotFoundError:
        data = default
    finally:
        return data

# Get from cache if possible, otherwise send request
def get(url):
    try:
        data = cache[url]
        print("LOADED FROM CACHE: " + url)
    except KeyError:
        req = request.urlopen(url)
        data = req.read().decode("utf-8")
        req.close()

        cache[url] = data
        print("CACHED: " + url)

    return data

#def save_image(url, filename):
#    request.urlretrieve(url, path.join(assets_dir, filename))


# ----- MAIN -----
# Create output dir
makedirs(output_dir, exist_ok=True)

# If this script was run before, suggest the previous username or osoc
old_user_or_org = read_txt(last_usage, "")
cache = read_txt(cache_file, dict())
if type(cache) is not dict:
    cache = loads(cache)



# Prompt oser for user or organisation name, create api URL
user_or_org = input("Insert username or organisation name [{0}]: ".format(old_user_or_org)) or old_user_or_org
if old_user_or_org is not user_or_org:
    with open(last_usage, "w") as file:
        file.writelines(user_or_org)

url = "https://api.github.com/users/{0}/repos".format(user_or_org)
image_url = "https://github.com/{0}.png"

# Get the data using Githubs API, parse JSON

data = loads(get(url))

repos = list()
for raw_repo in data:  
    # Get contributor data
    # If size == 0, assume repo is empty, skip
    if not raw_repo["size"]:
        continue
    raw_contributors = loads(get(raw_repo["contributors_url"]))
    contributors = list()
    for raw_contributor in raw_contributors:
        if raw_contributor["type"] == "Bot":
            continue
        contributor = {
            "name": raw_contributor["login"],
            "image": image_url.format(raw_contributor["login"]),
            "url": raw_contributor["html_url"]
        }
        contributors.append(contributor)

    # Save data used in output
    repo = {
        "name": raw_repo["name"],
        "repo-url": raw_repo["html_url"],
        "website-url": raw_repo["homepage"],
        "contributors": contributors
    }

    
    repos.append(repo)

with open(cache_file, "w", encoding="utf-8") as file:
    file.write(dumps(cache))

markdown = """
<link rel="stylesheet" href="https://unpkg.com/wingcss"/>
<link rel="stylesheet" href="stylesheet.css">

# Webportal for {name}
<img class="header" alt="Profile icon" src="{header_img}" />

---
<br><br>

""".format(name=user_or_org, header_img=image_url.format(user_or_org))

markdown_repo = """
## {repo_name}
##### {url_1} {url_2}
<br>
"""

markdown_contributors = """
[![{0[name]}'s profile picture]({0[image]})]({0[url]})"""

markdown_repo_url = "[Repo]({0})"
markdown_website_url = "[Website]({0})"

for repo in repos:
    name = repo["name"]
    repo_url = repo["repo-url"]
    website_url = repo["website-url"]


    # --- PROJECT URLS ---
    # If there's a website, set that url first
    if website_url:
        url_1 = markdown_website_url.format(website_url)
        url_2 = "- " + markdown_repo_url.format(repo_url)
    # If there's no website, just set the repo
    else:
        url_1 = markdown_repo_url.format(repo_url)
        url_2 = ""


    contributors = ""
    # --- CONTRIBUTOR URLS ---
    raw_contributors = repo["contributors"]
    for contributor in raw_contributors:
        contributors += markdown_contributors.format(contributor)


    # --- OUTPUT ---
    markdown += markdown_repo.format(
        repo_name=name,
        url_1=url_1,
        url_2=url_2
        ) + \
        """ 

        """ + contributors





    markdown += "<br><br>"


copy2("stylesheet.css", output_dir)

with open(site_filename, "w") as site:
    site.write(markdown)
