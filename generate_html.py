import os
import json
import time
import re
import datetime
import markdown2
from git import Repo

repo = Repo(".")
config = json.load(open("config.json"))
current_year = str(datetime.datetime.now().year)

# Define the HTML template with a placeholder for the Markdown filename
html_template = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" type="text/css" href="{base_site_url}/lib/bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="{base_site_url}/style.css">
    <link rel="stylesheet" href="//fonts.googleapis.com/css?family=Roboto:300,300italic,700,700italic">
    <link rel="stylesheet" href="//cdn.rawgit.com/necolas/normalize.css/master/normalize.css">
    <link rel="stylesheet" href="//cdn.rawgit.com/milligram/milligram/master/dist/milligram.min.css">
    <title>{filename}</title>
  </head>
  <body>
    <div class="container my-5">
    <a href="{base_site_url}/index.html" id="logo">{site_title}</a>
      <div class="row">
        <div class="col-md-6 mx-auto">
          <div class="mt-2" id="post">{post}</div>
        </div>
      </div>
      <div id="footer">Copyright {current_year}</div>
    </div>
  </body>
</html>
"""


import os
import glob
import shutil
import subprocess
import re


def process_tags(markdown_content):
    # Find all words that start with a hashtag and are not at the start of a line
    tags = re.findall(r"(?<!^)\B#\w\w+", markdown_content)
    # Remove the hashtag from the beginning of each tag and replace the markdown tag syntax with HTML
    tags_no_hash = [tag[1:] for tag in tags]
    for tag in tags:
        markdown_content = markdown_content.replace(
            tag, f"<span class='tag'>{tag[1:]}</span>"
        )
    return markdown_content, tags_no_hash


# Delete all files in 'generated' directory
shutil.rmtree("generated", ignore_errors=True)
# FIXME: should 'mv' first to a .bak directory, then delete the .bak directory only after the entire script succeeds, otherwise restore the .bak directory

# Create 'generated' and 'generated/posts' directories
os.makedirs("generated", exist_ok=True)
posts = dict()

# make a copy of the folder posts/assets to 'generated/assets'
shutil.copytree("posts/assets", "generated/assets")
shutil.copy("style.css", "generated/style.css")
shutil.copytree("lib", "generated/lib")


def get_git_creation_date(file_path):
    global repo
    commits_touching_path = list(repo.iter_commits(paths=file_path))
    if commits_touching_path:
        # The earliest commit is the last one in the list
        earliest_commit = commits_touching_path[-1]
        return earliest_commit.authored_datetime.strftime("%Y-%m-%d")  # change here
    return None


def get_git_modified_date(file_path):
    global repo
    commits_touching_path = list(repo.iter_commits(paths=file_path))
    if commits_touching_path:
        # The most recent commit is the first one in the list
        most_recent_commit = commits_touching_path[0]
        return most_recent_commit.authored_datetime.strftime("%Y-%m-%d")  # change here
    return None


# Iterate over all .md files in the 'posts' directory
for dirpath, dirnames, filenames in os.walk("posts"):
    for filename in filenames:
        if filename.endswith(".md") and "drafts" not in dirpath:
            # Extract the title and date from the Markdown file
            with open(os.path.join(dirpath, filename), "r") as f:
                markdown_content = f.read()
                markdown_content, tags = process_tags(
                    markdown_content
                )  # Process tags BEFORE converting markdown so the tags don't get read as H1s
                html_content = markdown2.markdown(markdown_content)
                title = re.search("<.*?>(.*?)</.*?>", html_content).group(1)
                created_time = get_git_creation_date(
                    os.path.join(dirpath, filename)
                )  # created time
                modified_time = get_git_modified_date(
                    os.path.join(dirpath, filename)
                )  # modified time

            # Generate the HTML content
            html_content = html_template.format_map(
                {
                    "base_site_url": config["base_site_url"],
                    "site_title": config["site_title"],
                    "filename": filename,
                    "post": html_content,
                    "current_year": current_year,
                }
            )

            # Write the HTML content to a new .html file in 'generated' directory
            if dirpath == "posts":
                generated_dir = "generated/" + "-".join(
                    filename.replace(".md", "").split()
                )
            else:
                generated_dir = os.path.join("generated", dirpath.replace("posts/", ""))

            # Add the post metadata to the dictionary
            post_path = generated_dir.replace("\\", "/").replace("generated/", "")
            posts[post_path] = {
                "title": title,
                "created": created_time,
                "modified": modified_time,
                # check "pages" array in config
                "isPage": post_path in config["pages"],
                "tags": tags,
            }

            # Generate the HTML for the tags
            tags_html = "".join(f"<span class='tag'>{tag}</span>" for tag in tags)

            # Insert the tags HTML below the H1 tag
            html_content = re.sub(
                r"</h1>",
                f"</h1>{tags_html}",
                html_content,
                flags=re.IGNORECASE,
            )

            os.makedirs(generated_dir, exist_ok=True)
            with open(
                os.path.join(generated_dir, "index.html"),
                "w",
            ) as f:
                f.write(html_content)

            # If the extension is a photo or PDF, copy it to the same location under 'generated'
            if filename.endswith((".jpg", ".png", ".pdf")):
                shutil.copy(
                    os.path.join(dirpath, filename),
                    os.path.join(generated_dir, filename),
                )


# Write the post metadata to a JSON file
with open("generated/manifest.json", "w") as f:
    json.dump(posts, f)

# Generate an XML sitemap using the post manifest
sitemap_template = """
<?xml version="1.0" encoding="UTF-8"?>
<urlset
  xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
  http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
{}
</urlset>
"""

sitemap_url_template = """ 
  <url>
    <loc>{}</loc>
    <lastmod>{}</lastmod>
  </url>
"""

sitemap_urls = [
    sitemap_url_template.format(
        f"{config['base_site_url']}/{os.path.splitext(filename)[0]}.html",
        posts[filename]["modified"],
    )
    for filename in posts
]

sitemap_content = sitemap_template.format("\n".join(sitemap_urls))

with open("generated/sitemap.xml", "w") as f:
    f.write(sitemap_content)


# Update homepage
def update_index_html():
    global current_year

    # Load the existing HTML
    with open("homepage.html", "r") as html_file:
        html = html_file.read()

    site_name = (
        config["site_title"]
        if config["site_title"]
        else "Update site_title in config.json"
    )

    # Update the HTML with the new title
    updated_html = re.sub(
        r"BLOG_NAME_WILL_BE_OVERWRITTEN",
        f"{site_name}",
        html,
        flags=re.IGNORECASE,
    )

    updated_html = re.sub(
        r'<a href="index.html" id="logo">BLOG_NAME_WILL_BE_OVERWRITTEN</a>',
        f'<a href="index.html" id="logo">{site_name}</a>',
        updated_html,
        flags=re.IGNORECASE,
    )

    updated_html = re.sub(
        r"GOOGLE_SITE_VERIFICATION_WILL_BE_OVERWRITTEN",
        f'{config["google_search_console_site_verification"]}',
        updated_html,
        flags=re.IGNORECASE,
    )

    # replace 'CURRENT_YEAR_WILL_BE_OVERWRITTEN' with current year
    updated_html = re.sub(
        r"CURRENT_YEAR_WILL_BE_OVERWRITTEN",
        current_year,
        updated_html,
        flags=re.IGNORECASE,
    )

    # Write the updated HTML to the generated index.html file
    with open("generated/index.html", "w") as html_file:
        html_file.write(updated_html)


# Call the function in your script
update_index_html()
