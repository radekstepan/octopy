#!/usr/bin/python
# -*- coding: utf -*-

import sys, os, codecs, unicodedata, re, datetime, time, markdown as markup, shutil
from jinja2 import Environment, PackageLoader

def install():
    """
    Configure the app
    """
    cfg = {
        'TITLE': 'octopy',
        'SUBTITLE': 'A static site generator',
        'LATEST_POSTS': 3,
        'POST_PREVIEW_CUTOFF': 250, # after how many chars to try to cutoff a post preview from listing
        'SOURCE_DIR': '',
        'POSTS_DIR': '',
        'PUBLIC_DIR': '',
        'BASE_URL': '',
        'COPY_DIRS': ('css', 'img', 'js')
    }

    # site title
    while True:
        cfg['TITLE'] = raw_input('Site title, used in the header and title tags ').strip()
        if cfg['TITLE']:
            break

    # site subtitle
    while True:
        cfg['SUBTITLE'] = raw_input('Site subtitle, a description used in the header ').strip()
        if cfg['SUBTITLE']:
            break

    # latest posts on index
    while True:
        cfg['LATEST_POSTS'] = int(raw_input('How many latest posts to show ').strip())
        if cfg['LATEST_POSTS']:
            break

    # source directory
    while True:
        cfg['SOURCE_DIR'] = raw_input('Source directory (usually \'source\') ').strip().strip('/')
        if cfg['SOURCE_DIR']:
            break

    # posts directory
    while True:
        cfg['POSTS_DIR'] = raw_input('Posts directory within source directory (usually \'blog\') ').strip().strip('/')
        if cfg['POSTS_DIR']:
            break

    # public (target) directory
    while True:
        cfg['PUBLIC_DIR'] = raw_input('Public directory with published content (usually \'public\') ').strip().strip('/')
        if cfg['PUBLIC_DIR']:
            break

    # base url for the site
    while True:
        cfg['BASE_URL'] = raw_input('Base url for the site (e.g. \'http://localhost\') ').strip().strip('/')
        if cfg['BASE_URL']:
            cfg['BASE_URL'] += "/%s/" % cfg['PUBLIC_DIR']
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


def date_filter(value):
    """
    A Jinja filter for displaying dates from Yaml value
    """
    def suffix(day):
        if day in (11, 12, 13):
            return 'th'
        else:
            day %= 10
        if day == 1:
            return 'st'
        if day == 2:
            return 'nd'
        if day == 3:
            return 'rd'
        return 'th'

    # format
    value = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M').strftime('%b %d %Y').split()
    # st, nd, rd, th suffix
    value[1] = '%s%s,' % (value[1].lstrip('0'), suffix(int(value[1])))
    return ' '.join(value)

def markdown(text):
    """
    Spit out HTML from Markdown syntax (with code tag fixes)
    """
    return markup.markdown(text.replace("<code>", "<code>\n"))

class Octopy:

    # these key value pairs are allowed in source
    allowed_meta = ['layout', 'title', 'date', 'publish', 'categories']

    def __init__(self):
        self.dir = os.getcwd()
        self.date = datetime.datetime.now()
        self.hourminute = ":".join(['%02d' % self.date.hour, '%02d' % self.date.minute])

        # Jinja
        self.jinja = Environment(loader=PackageLoader('octopy', 'templates'))
        self.jinja.filters['date'] = date_filter

    def new_post(self, title):
        """
        Create a new blog post
        """
        import config

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
                f.write('---\nlayout: post\ntitle: %s\ndate: %i-%i-%i %s\ncategories: \n---\n' %
                        (title, self.date.year, self.date.month, self.date.day, self.hourminute))
            print 'Post created.\n'

    def new_page(self, title):
        """
        Create a new page
        """
        import config
        
        # slugify
        path = "/".join([config.SOURCE_DIR, slugify(title)])
        # page exists?
        if os.path.isfile(path + "/index.markdown"):
            print 'This page already exists.\n'
        else:
            # create directories
            os.makedirs(path)
            # create page.markdown
            with open(path + "/index.markdown", 'w') as f:
                f.write('---\nlayout: page\ntitle: %s\ndate: %i-%i-%i %s\n---\n' %
                        (title, self.date.year, self.date.month, self.date.day, self.hourminute))
            print 'Page created.\n'

    def publish(self):
        """
        Publish all content from source dir
        """
        import config

        index, categories = [], set()
        # recursively go through source directories
        for e in os.walk(config.SOURCE_DIR):
            # is file?
            if len(e[-1]) > 0:
                # is .markdown?
                if e[-1][0].endswith('.markdown'):
                    # read file
                    with codecs.open("/".join([e[0], e[-1][0]]), 'r', 'utf-8') as f:
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
                                    meta[key] = line[s+1:].strip()
                    # check if we can publish
                    if 'publish' in meta and meta['publish'] != 'true':
                        continue
                    # categories
                    if 'categories' in meta:
                        meta['categories'] = [slugify(c) for c in meta['categories'].split(',') if len(c) > 0]
                        categories = categories.union(set(meta['categories']))
                    # figure target directory and published directory
                    public_path = e[0].split('/')
                    meta['path'] = '/'.join([public_path[x] for x in range(1, len(public_path))])
                    public_path[0] = config.PUBLIC_DIR
                    public_path = "/".join(public_path)
                    # create directory structure in public dir if needed
                    if not os.path.isdir(public_path):
                        os.makedirs(public_path)
                    # parse the source file from Markdown
                    content = markdown(markup)
                    # call Jinja
                    if meta['layout'] == 'post':
                        template = self.jinja.get_template('posts/post.html')
                    else:
                        template = self.jinja.get_template('pages/page.html')
                    html = template.render(content=content, meta=meta, base_url=config.BASE_URL, title=config.TITLE,
                                           subtitle=config.SUBTITLE, page_title=meta['title'])
                    # write the html
                    with codecs.open(public_path + "/index.html", 'w', 'utf-8') as f:
                        f.write(html)
                    # save to site index if is post
                    if meta['layout'] == 'post':
                        # preview for homepage?
                        i = config.POST_PREVIEW_CUTOFF
                        content = []
                        for block in markup.split('\n\n'):
                            i -= len(block)
                            content.append(block)
                            if i < 0:
                                meta['more_content'] = True
                                break
                        meta['content'] = markdown('\n\n'.join(content))
                        index.append(meta)
        if index:
            # sort
            index = sorted(index,
                           key=lambda post_date: time.mktime(time.strptime(post_date['date'], "%Y-%m-%d %H:%M")),
                           reverse=True)

            # latest posts
            latest = index[:config.LATEST_POSTS if config.LATEST_POSTS < len(index) else len(index)]

            # should we display an archive?
            archive_link = None
            if latest < index:
                archive_link = config.BASE_URL+config.POSTS_DIR+'/archives'

                # call Jinja for archive
                template = self.jinja.get_template('posts/archive.html')
                html = template.render(base_url=config.BASE_URL, posts_dir=config.POSTS_DIR, title=config.TITLE,
                                       subtitle=config.SUBTITLE, posts=index)
                # write the html
                archives_dir = '/'.join([config.PUBLIC_DIR , config.POSTS_DIR, "archives"])
                if not os.path.isdir(archives_dir):
                    os.makedirs(archives_dir)
                with codecs.open(archives_dir + "/index.html", 'w', 'utf-8') as f:
                    f.write(html)

            # categories
            for category in categories:
                # call Jinja for archive
                template = self.jinja.get_template('posts/category.html')
                html = template.render(base_url=config.BASE_URL, posts_dir=config.POSTS_DIR, title=config.TITLE,
                                       subtitle=config.SUBTITLE, category=category,
                                       posts=[p for p in index if category in p['categories']])
                # write the html
                archives_dir = '/'.join([config.PUBLIC_DIR , config.POSTS_DIR, "categories", category])
                if not os.path.isdir(archives_dir):
                    os.makedirs(archives_dir)
                with codecs.open(archives_dir + "/index.html", 'w', 'utf-8') as f:
                    f.write(html)

            # call Jinja for index
            template = self.jinja.get_template('posts/index.html')
            html = template.render(posts=latest, base_url=config.BASE_URL, title=config.TITLE, subtitle=config.SUBTITLE,
                                   archive_link=archive_link)
            # write the html
            with codecs.open(config.PUBLIC_DIR + "/index.html", 'w', 'utf-8') as f:
                f.write(html)

        # copy over css, js, img
        for d in config.COPY_DIRS:
            if os.path.isdir('templates/%s' % d):
                for e in os.walk('templates/%s' % d):
                    if e[-1]:
                        target_dir = e[0].replace('templates/', '%s/' % config.PUBLIC_DIR)
                        if not os.path.exists(target_dir):
                            os.makedirs(target_dir)
                        for f in e[-1]:
                            shutil.copyfile('/'.join([e[0], f]), '/'.join([target_dir, f]))
        
        print 'Source published.\n'

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1].strip()

        if command.find("new_post") > -1:
            p = Octopy()
            p.new_post(command[command.find('[') + 1:command.find(']')])
        elif command.find("new_page") > -1:
            p = Octopy()
            p.new_page(command[command.find('[') + 1:command.find(']')])
        elif command.find('publish') > -1:
            p = Octopy()
            p.publish()
        elif command.find('install') > -1:
            install()
        else:
            print '\nTask not recognized.\n'