#!/usr/bin/python
# -*- coding: utf -*-

import random, os

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

cfg['SECRET_KEY'] = ''.join([random.choice('./ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') for i in range(30)])

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