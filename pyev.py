#!/usr/bin/python
# -*- coding: utf -*-

import sys, os, unicodedata, re, datetime
import config
from jinja2 import Environment, PackageLoader

def install():
    """
    Configure the app
    """
    cfg = {
        'SOURCE_DIR': '',
        'POSTS_DIR': '',
        'PUBLIC_DIR': ''
    }

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
        # recursively go through source directories
        for e in os.walk(config.SOURCE_DIR):
            # is file?
            if len(e[-1]) > 0:
                # is .markdown?
                if e[-1][0].endswith('.markdown'):
                    # read file
                    with open("/".join([e[0], e[-1][0]]), 'r') as f:
                        markdown = f.read()
                    # TODO: check if we can publish
                    # create directory structure in public dir if needed
                    public_path = "/".join([config.PUBLIC_DIR, e[0]])
                    if not os.path.isdir(public_path):
                        os.makedirs(public_path)
                    # TODO: skip Yaml from source
                    # TODO: parse the source file from Markdown
                    # TODO: call Jinja
                    template = self.jinja.get_template('posts/post.html')
                    html = template.render(the='variables', go='here')
                    # write the html
                    with open(public_path + "/index.html", 'w') as f:
                        f.write(html)
        # TODO: create site index
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