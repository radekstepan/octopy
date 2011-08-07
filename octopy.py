#!/usr/bin/python
# -*- coding: utf -*-

import sys, os, unicodedata, re, datetime, config, markdown
from jinja2 import Environment, PackageLoader

def install():
    """
    Configure the app
    """
    cfg = {
        'LATEST_POSTS': 3,
        'SOURCE_DIR': '',
        'POSTS_DIR': '',
        'PUBLIC_DIR': ''
    }

    # latest posts on index
    while True:
        cfg['LATEST_POSTS'] = int(raw_input('How many latest posts to show ').strip())
        if cfg['LATEST_POSTS']:
            break

    # source directory
    while True:
        cfg['SOURCE_DIR'] = raw_input('Source directory (usually \'source\') ').strip()
        if cfg['SOURCE_DIR']:
            break

    # posts directory
    while True:
        cfg['POSTS_DIR'] = raw_input('Posts directory within source directory (usually \'_posts\') ').strip()
        if cfg['POSTS_DIR']:
            break

    # public (target) directory
    while True:
        cfg['PUBLIC_DIR'] = raw_input('Public directory with published content (usually \'public\') ').strip()
        if cfg['PUBLIC_DIR']:
            break

    python_code = []
    for key, value in cfg.items():
        if isinstance(value, str):
            value = "'" + value.replace("'", r"\'") + "'"
        elif isinstance(value, list):
            value = '[]'
        python_code.append("%s = %s" % (key, value))

    with open(os.getcwd() + '/config.py', 'w') as f:
        f.write('\n'.join(python_code))

    print '\nConfiguration file written successfully.\n'

def slugify(value):
    """
    Slugify an input text (Django style)
    """
    if isinstance(value, unicode):
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

class Pyev:

    # these key value pairs are allowed in source
    allowed_meta = {'layout', 'title', 'date', 'publish'}

    def __init__(self):
        self.dir = os.getcwd()
        self.date = datetime.datetime.now()
        self.jinja = Environment(loader=PackageLoader('pyev', 'templates'))

    def new_post(self, title):
        """
        Create a new blog post
        """
        # generate date and slugify
        path = "/".join([config.SOURCE_DIR, config.POSTS_DIR,
                         str(self.date.year), str(self.date.month), str(self.date.day), slugify(title)])
        # post exists?
        if os.path.isfile(path + "/index.markdown"):
            print 'This post already exists.\n'
        else:
            # create directories
            os.makedirs(path)
            # create post.markdown
            with open(path + "/index.markdown", 'w') as f:
                f.write('---\nlayout: post\ntitle: "%s"\ndate: %i-%i-%i %i:%i\n---\n' %
                        (title, self.date.year, self.date.month, self.date.day, self.date.hour, self.date.minute))
            print 'Post created.\n'

    def publish(self):
        """
        Publish all content from source dir
        """
        index = []
        # recursively go through source directories
        for e in os.walk(config.SOURCE_DIR):
            # is file?
            if len(e[-1]) > 0:
                # is .markdown?
                if e[-1][0].endswith('.markdown'):
                    # read file
                    with open("/".join([e[0], e[-1][0]]), 'r') as f:
                        markup = f.read()
                    # read and skip Yaml from source
                    meta = {'slug': e[0].split('/')[-1]}
                    src = markup.split('\n')
                    if src[0] == '---':
                        for i in range(1, len(src)):
                            line = src[i]
                            if line == '---':
                                # end the header and strip from source
                                markup = '\n'.join([src[x] for x in range(i+1, len(src))])
                                break
                            # parse allowed meta
                            s = line.find(':')
                            if s > -1:
                                key = line[:s].strip()
                                if key in self.allowed_meta:
                                    meta[key] = line[s+1:]
                    # check if we can publish
                    if 'publish' in meta and meta['publish'] != 'true':
                        continue
                    # figure target directory
                    public_path = e[0].split('/')
                    public_path[0] = config.PUBLIC_DIR
                    public_path = "/".join(public_path)
                    # create directory structure in public dir if needed
                    if not os.path.isdir(public_path):
                        os.makedirs(public_path)
                    # parse the source file from Markdown
                    content = markdown.markdown(markup)
                    # call Jinja
                    template = self.jinja.get_template('posts/post.html')
                    html = template.render(content=content, meta=meta)
                    # write the html
                    with open(public_path + "/index.html", 'w') as f:
                        f.write(html)
                    # save to site index
                    meta['content'] = content
                    index.append(meta)
        if index:
            # latest posts
            latest = [index[x] for x in range(config.LATEST_POSTS if config.LATEST_POSTS < len(index) else len(index))]
            # call Jinja
            template = self.jinja.get_template('posts/index.html')
            html = template.render(posts=latest)
            # write the html
            with open(config.PUBLIC_DIR + "/index.html", 'w') as f:
                f.write(html)
        print 'Source published.\n'

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1].strip()

        if command.find("new_post") > -1:
            p = Pyev()
            p.new_post(command[command.find('[') + 1:command.find(']')])
        elif command.find('publish') > -1:
            p = Pyev()
            p.publish()
        elif command.find('install') > -1:
            install()
        else:
            print '\nTask not recognized.\n'