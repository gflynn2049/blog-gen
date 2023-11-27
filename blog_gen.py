import os
import sys
from datetime import datetime
import json
import yaml
from jinja2 import Environment, FileSystemLoader
import markdown
from slugify import slugify
import subprocess
import shutil
from bs4 import BeautifulSoup

def load_config():
    with open('config/config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_markdown_template(template_path):
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def generate_new_draft(title, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    file_name = f"{slugify(title)}.md"
    output_path = os.path.join(output_dir, file_name)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f'title: {title}\n')
        f.write(f'date: {datetime.now().strftime("%Y-%m-%d")}\n')
        f.write('---\n\n')
        
def build_html_from_markdown(input_dir, output_dir, template_path):
    config = load_config()  

    # rm all files in the output directory
    for file_name in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file_name)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    markdown_files = [f for f in os.listdir(input_dir) if f.endswith('.md')]

    posts_output_dir = os.path.join(output_dir, 'posts')
    os.makedirs(posts_output_dir, exist_ok=True)

    # load HTML template
    template_content = load_markdown_template(template_path)
    env = Environment(loader=FileSystemLoader('.'))
    template = env.from_string(template_content)

    posts = []

    for markdown_file in markdown_files:
        input_path = os.path.join(input_dir, markdown_file)
        output_file_name = os.path.splitext(markdown_file)[0] + '.html'
        output_path = os.path.join(posts_output_dir, output_file_name)

        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # extract markdown classes
        post_content_html = extract_markdown_classes(content)
        metadata, post_content = content.split('---\n', 1)
        metadata = yaml.safe_load(metadata)

        rendered_content = template.render(
            post={
                'title': metadata.get('title', ''),
                'date': metadata.get('date', ''),
                'content': post_content_html,
                'author_name': config.get('author_name', ''),
                'author_website': config.get('author_website', ''),
            }
        )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered_content)

        posts.append({
            'title': metadata.get('title', ''),
            'date': metadata.get('date', ''),
            'link': f'posts/{output_file_name}',  # link to the post
        })

    generate_index_page(posts)

    subprocess.run(['npx', 'tailwindcss', 'build', 'style/post.css', '-o', 'output/posts/post.css'])
    subprocess.run(['npx', 'tailwindcss', 'build', 'style/index.css', '-o', 'output/index.css'])
    
def extract_markdown_classes(content):
    markdown_classes = {
        "h1": "heading1",
        "h2": "heading2",
        "h3": "heading3",
        "h4": "heading4",
        "h5": "heading5",
        "h6": "heading6",
        "p": "paragraph",
        "blockquote": "blockquote",
        "code": "codeBlock",
        "ul": "list",
        "li": "listItem",
        "hr": "hr",
        "pre": "codeBlock",
        "strong": "bold",
        "em": "italic",
        "a": "link",
        "inlineCode": "inlineCode",
    }

    post_content_html = markdown.markdown(content, output_format="html")

    soup = BeautifulSoup(post_content_html, "html.parser")
    for tag in soup.find_all():
        if tag.name in markdown_classes:
            tag["class"] = [markdown_classes[tag.name]] + tag.get("class", [])

    return str(soup)

def generate_index_page(posts):
    config = load_config()  
    
    # load index template
    index_template_content = load_markdown_template("templates/index_template.html")
    index_template = Environment(loader=FileSystemLoader('.')).from_string(index_template_content)

    # render index template
    index_rendered_content = index_template.render(
        site_name=config.get('site_name', ''),
        author_name=config.get('author_name', ''),
        author_website=config.get('author_website', ''),
        posts=posts
    )

    index_output_path = os.path.join('output', 'index.html')
    with open(index_output_path, 'w', encoding='utf-8') as f:
        f.write(index_rendered_content)

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("usage: python blog_gen.py new <name> | build")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "new":
        if len(sys.argv) < 3:
            print("usage: python blog_gen.py new <name>")
            sys.exit(1)
        title = sys.argv[2]
        generate_new_draft(title, "markdown/draft")
        print(f"draft '{title}' created successfully.")

    elif command == "build":
        build_html_from_markdown(
            "markdown/post", "output", "templates/post_template.html"
        )
        print("html files built successfully")

    else:
        print("unknown command. usage: python blog_gen.py new <name> | build")
        sys.exit(1)
