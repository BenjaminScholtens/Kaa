import os
import json
import time

config = json.load(open("config.json"))

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
    <a href="{base_site_url}/index.html" id="logo">Your Blog Name</a>
      <div class="row">
        <div class="col-md-6 mx-auto">
          <div class="mt-2" id="post"></div>
        </div>
      </div>
      <div id="footer">Copyright 2023</div>
    </div>
    <script src="{base_site_url}/lib/showdown.min.js"></script>
    <script type="module">
      fetch("{base_site_url}/posts/{post_path}")
        .then(response => response.text())
        .then(data => {{
          const post = data;
          document.getElementById("post").innerHTML = new showdown.Converter().makeHtml(post);
        }})
        .catch(error => {{
          console.error("Error:", error);
        }});
    </script>
  </body>
</html>
"""

import os
import glob
import shutil

# Delete all files in 'generated' directory
shutil.rmtree("generated", ignore_errors=True)

# Create 'generated' and 'generated/posts' directories
os.makedirs("generated/posts", exist_ok=True)
posts = dict()

# make a copy of the folder posts/assets to 'generated/assets'
shutil.copytree("posts/assets", "generated/assets")

# Iterate over all .md files in the 'posts' directory
for dirpath, dirnames, filenames in os.walk("posts"):
    for filename in filenames:
        if filename.endswith(".md"):
            # Extract the title and date from the Markdown file
            with open(os.path.join(dirpath, filename), "r") as f:
                title = f.readline().strip().lstrip("# ")
                created_time = time.ctime(
                    os.path.getctime(os.path.join(dirpath, filename))
                )  # created time
                modified_time = time.ctime(
                    os.path.getmtime(os.path.join(dirpath, filename))
                )  # modified time
            # Add the post metadata to the dictionary
            posts[os.path.join(dirpath, filename).replace("\\", "/")] = {
                "title": title,
                "created": created_time,
                "modified": modified_time,
            }
            
            # Check if file has been updated. If not, skip rest of loop iteration 
            if os.path.exists(os.path.join("generated", dirpath, f"{os.path.splitext(filename)[0]}.html")):
                if os.path.getmtime(os.path.join(dirpath, filename)) < os.path.getmtime(os.path.join("generated", dirpath, f"{os.path.splitext(filename)[0]}.html")):
                    continue
            
            # Generate the HTML content
            html_content = html_template.format_map(
                {
                    "base_site_url": config["base_site_url"],
                    "filename": filename,
                    "post_path": os.path.join(dirpath, filename).replace("\\", "/"),
                }
            )

            # Write the HTML content to a new .html file in 'generated/posts' directory
            generated_dir = os.path.join("generated", dirpath)
            os.makedirs(generated_dir, exist_ok=True)
            with open(
                os.path.join(generated_dir, f"{os.path.splitext(filename)[0]}.html"),
                "w",
            ) as f:
                f.write(html_content)

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
        f"{config['base_site_url']}/{os.path.splitext(filename)[0]}.html",
        posts[filename]["modified"],
    )
    for filename in posts
]

sitemap_content = sitemap_template.format("\n".join(sitemap_urls))

with open("generated/sitemap.xml", "w") as f:
    f.write(sitemap_content)
