<img src="./posts/assets/kaa-logo.png" alt="My Image" width="200" style="max-width: 100%; display: block; margin: auto;"/>

# Kaa
Welcome to Kaa - a Python-based HTML blog generator! Convert your Markdown to structured HTML blogs.

## Usage

### Installation

Install using `pip install -r requirements.txt`.

### Add a new blog post

Create a new post in the `posts` directory. Call it whatever you like.

The first line of the file will be the **title** of the blog post. The **date** will be automatically populated from the time you created or modified the file.

The rest of the file should be the content of the blog post in Markdown format.

## Generating the HTML with `build.sh`

After cloning the repository, you can use the following command to build your blog from markdown files if you're doing this for the first time (`chmod` is necessary to allow the build script to be executed, but you only need to do this once):

```bash
chmod +x build.sh && ./build.sh
```

After the first time, you can just run the following command to build your blog:

```bash
./build.sh
```

If you prefer, or you have special Python environment requirements, you can also run the following command to build your blog:

```bash
python3 generate_html
```

## Accessing your Blog on the Web

You can deploy your blog to a service like Vercel, Netlify, or Heroku.

If your chosen service supports build steps, you can instruct the service to run `build.sh` or `python3 generate_html` before deploying your blog, and then you don't even need to build it! Of course, it only takes a second to build, and then you can identify any errors that might pop up, but to each their own!

## Features

- [x] Markdown to HTML conversion
- [x] Automatic sitemap generation
- [x] Easy URL configuration in `config.json` 