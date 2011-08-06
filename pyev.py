#!/usr/bin/python
# -*- coding: utf -*-

import sys, os, unicodedata, re, datetime
import config

class Utils:

    def slugify(self, value):
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

    def install(self):
        """
        Configure the app
        """
        cfg = {
            'SOURCE_DIR': '',
            'POSTS_DIR': ''
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

    def new_post(self, title):
        """
        Create a new blog post
        """
        # generate date and slugify
        u = Utils()
        path = "/".join([config.SOURCE, config.POSTS,
                         str(self.date.year), str(self.date.month), str(self.date.day), u.slugify(title)])
        # post exists?
        if os.path.isfile(path + "/post.markdown"):
            print 'This post already exists.\n'
        else:
            # create directories
            os.makedirs(path)
            # create post.markdown
            with open(path + "/post.markdown", 'w') as f:
                f.write('---\nlayout: post\ntitle: "%s"\ndate: %i-%i-%i %i:%i\n---\n' %
                        (title, self.date.year, self.date.month, self.date.day, self.date.hour, self.date.minute))
            print 'Post created.\n'

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1].strip()
        p = Pyev()

        if command.find("new_post") > -1:
            p.new_post(command[command.find('[') + 1:command.find(']')])
        elif command.find('install') > -1:
            p.install()
        else:
            print '\nTask not recognized.\n'