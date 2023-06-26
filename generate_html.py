import os
import json
import time
import re
import datetime
import markdown2

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
    date_str = (
        subprocess.check_output(
            [
                "git",
                "log",
                "--diff-filter=A",
                "--follow",
                "--format=%aD",
                "-1",
                file_path,
            ]
        )
        .decode("utf-8")
        .strip()
    )

    return date_str


def get_git_modified_date(file_path):
    date_str = (
        subprocess.check_output(
            ["git", "log", "--follow", "--format=%aD", "-1", file_path]
        )
        .decode("utf-8")
        .strip()
    )

    return date_str


# Iterate over all .md files in the 'posts' directory
for dirpath, dirnames, filenames in os.walk("posts"):
    for filename in filenames:
        if filename.endswith(".md") and "drafts" not in dirpath:
            # Extract the title and date from the Markdown file
            with open(os.path.join(dirpath, filename), "r") as f:
                markdown_content = f.read()
                html_content = markdown2.markdown(markdown_content)
                title = (
                    html_content.split("\n", 1)[0]
                    .strip()
                    .lstrip("<h1>")
                    .rstrip("</h1>")
                )
                created_time = get_git_creation_date(
                    os.path.join(dirpath, filename)
                )  # created time
                modified_time = get_git_modified_date(
                    os.path.join(dirpath, filename)
                )  # modified time
            # Add the post metadata to the dictionary
            posts[
                os.path.join(dirpath, filename).replace("\\", "/").replace("posts/", "")
            ] = {
                "title": title,
                "created": created_time,
                "modified": modified_time,
            }

            # Check if file has been updated. If not, skip rest of loop iteration
            if os.path.exists(
                os.path.join(
                    "generated", dirpath, f"{os.path.splitext(filename)[0]}.html"
                )
            ):
                if os.path.getmtime(os.path.join(dirpath, filename)) < os.path.getmtime(
                    os.path.join(
                        "generated", dirpath, f"{os.path.splitext(filename)[0]}.html"
                    )
                ):
                    continue

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
            generated_dir = os.path.join("generated", dirpath.replace("posts/", ""))
            os.makedirs(generated_dir, exist_ok=True)
            with open(
                os.path.join(generated_dir, f"{os.path.splitext(filename)[0]}.html"),
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
with open("generated/posts.json", "w") as f:
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
        f"{config['base_site_url']}/{os.path.splitext(filename.replace('posts/', ''))[0]}.html",
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
