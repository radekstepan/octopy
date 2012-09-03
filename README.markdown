# Octopy (August 2011)

A blog aware static site generator. Did anyone say [Octopress](http://octopress.org) in Python?

![image](https://github.com/radekstepan/octopy/raw/master/example.png)

## Requirements

* Jinja2, used for templating
* Markdown, used for markup
* Pygments, used for code highlighting

## Getting started

First setup the app by calling:

```bash
$ ./octopy.py install
```

You will be asked a series of questions. One of them is the location of your source directory which is `source` by default. This is the place where your pages and posts will be created.

## Syntax

The syntax pretty much follows that of Octopress.

To create a **static page** execute the following:

```bash
$ ./octopy.py new_page["title"]
```

To create a **blog post** execute the following:

```bash
$ ./octopy.py new_post["title"]
```

To publish the result into HTML, execute the following:

```bash
$ ./octopy.py publish
```