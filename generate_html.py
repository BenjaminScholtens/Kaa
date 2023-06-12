import os
import json
import time

# Define the HTML template with a placeholder for the Markdown filename
html_template = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" type="text/css" href="../../lib/bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="../../style.css">
    <link rel="stylesheet" href="//fonts.googleapis.com/css?family=Roboto:300,300italic,700,700italic">
    <link rel="stylesheet" href="//cdn.rawgit.com/necolas/normalize.css/master/normalize.css">
    <link rel="stylesheet" href="//cdn.rawgit.com/milligram/milligram/master/dist/milligram.min.css">
    <title>{}</title>
  </head>
  <body>
    <div class="container my-5">
    <a href="../../index.html" id="logo">Your Blog Name</a>
      <div class="row">
        <div class="col-md-6 mx-auto">
          <div class="mt-2" id="post"></div>
        </div>
      </div>
      <div id="footer">Copyright 2023</div>
    </div>
    <script src="../../lib/showdown.min.js"></script>
    <script type="module">
      fetch("../../posts/{}")
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

# Iterate over all .md files in the 'posts' directory
for filename in os.listdir("posts"):
    if filename.endswith(".md"):
        # Generate the HTML content
        html_content = html_template.format(filename, filename)
        # Write the HTML content to a new .html file in 'generated/posts' directory
        with open(f"generated/posts/{os.path.splitext(filename)[0]}.html", "w") as f:
            f.write(html_content)
        # Extract the title and date from the Markdown file
        with open(f"posts/{filename}", "r") as f:
            title = f.readline().strip().lstrip("# ")
            created_time = time.ctime(
                os.path.getctime(f"posts/{filename}")
            )  # created time
            modified_time = time.ctime(
                os.path.getmtime(f"posts/{filename}")
            )  # modified time
        # Add the post metadata to the dictionary
        posts[filename] = {
            "title": title,
            "created": created_time,
            "modified": modified_time,
        }

# Write the post metadata to a JSON file
with open("generated/posts.json", "w") as f:
    json.dump(posts, f)
