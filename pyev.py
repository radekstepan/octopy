#!/usr/bin/python
# -*- coding: utf -*-

import sys, os, unicodedata, re

class Utils:

    def slugify(self, value):
        """
        Slugify an input text (Django style)
        """
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
        return re.sub('[-\s]+', '-', value)

class Pyev:

    def install(self):
        """
        Configure the app
        """
        # config settings to save
        cfg = {
            'FLASK_PORT' : 5000,
            'DEBUG' : True,
            'SECRET_KEY' : ''
        }

        # flask app port
        while True:
            cfg['FLASK_PORT'] = int(raw_input('Flask app port (usually 5000) ').strip())
            if cfg['FLASK_PORT']:
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

        print('\nConfiguration file written successfully.\n')

    def new_post(self, title):
        """
        Create a new blog post
        """
        print title

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