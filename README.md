# blog-gen

blog-gen is a simple tool written in Python for generating static HTML blog pages from Markdown files.


## usage
Create a New Draft:

```bash
python blog_gen.py new "Your Blog Title" # generate a new draft in markdown/draft
```

before building, move ready-to-post drafts into `markdown/post` folder

build HTML Files:

```bash
python blog_gen.py build
```

## customization

modify the templates in the templates folder to customize the appearance of your blog.
adjust the styles in the style folder to change the look and feel.


## todo

- [ ] render drafts flag
- [ ] image style 