import collections
from datetime import datetime, timedelta
import itertools
import json
import os
import pickle
import shutil
import subprocess
import sys
import urllib

import common

NEWS_TIMESPAN = 30 # news from last 30 days
DB_PICKLED = 'databags/news.pickle'

def pandoc(data):
    if not shutil.which('pandoc'):
        raise OSError(("Couldn't find Pandoc on the path, which is required "
                "for converting the changelog."))
    proc = subprocess.Popen(['pandoc', '-f', 'markdown', '-t', 'html'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    html = proc.communicate(data.encode(sys.getdefaultencoding()))[0] \
            .decode(sys.getdefaultencoding())
    if not proc.wait() == 0:
        raise OSError("Pandoc exited unsuccessfully, aborting.")
    return html

def get_releases(timespan):
    """Return all releases made in the given timedelta."""
    releases = {}
    now = datetime.now()
    # dictionaries have a name, other entries such as `software` don't
    dictionaries = [item for item in common.load_json_api() if 'name' in item]
    for dictionary in dictionaries:
        name = dictionary['name']
        for release in dictionary['releases']:
            date = datetime.strptime(release['date'], '%Y-%m-%d')
            if (now - date) < timespan:
                if name not in releases:
                    releases[name] = (date, release['version'])
                elif releases[name][0] < date: # replace with newer
                    releases[name] = (date, release['version'])
    return collections.OrderedDict(sorted(releases.items(),
            key=lambda kv: kv[1][0]))

def github_request(path):
    """Make a GitHub API request and return aJSON object."""
    url = "https://api.github.com/{}".format( path.lstrip('/'))
    request_headers = {'User-Agent': 'freedict'}
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request) as f:
        return json.loads(f.read().decode('UTF-8'))

def get_events_for_repo(repo):
    """Get all public events for a public GitHub repository."""
    events = {}
    def append(key, value):
        if key not in events:
            events[key] = []
        events[key].append(value)

    # iterate over events
    for event in github_request('/repos/freedict/{}/events'.format(repo)):
        date = datetime.strptime(event['created_at'].split("T")[0],
                '%Y-%m-%d')
        type = event['type']
        if type == 'GollumEvent':
            for page in event['payload']['pages']:
                append(type, (date, page['title'], page['html_url']))
        elif type == 'PushEvent':
            append(type, (date, int(event['payload']['size'])))
        elif type in ('IssueCommentEvent', 'IssuesEvent'):
            append('IssueEvent', date) # only use IssueEvent
        # else: unhandled
    return events

def format_news(news):
    """Format the entries gathered in the generate_news_section function."""
    if len(news) == 2 and not news['releases']:
        return '' # no news, no news section; please don't let this happen :)

    # load localised language names
    languages = {id: _(name) for id, name in common.load_iso_table().items()}
    def trans_name(name):
        lg1, lg2 = name.split('-') # ISO 639-3 xxx-yyy naming
        return '%s - %s' % (languages[lg1], languages[lg2])

    page = ['<h3>%s</h3>\n\n<dl>' % _("What's Happening")]
    for date, description in news['changelog'].items():
        page.append('<dt><strong>%s</strong></dt>\n<dd><p>%s</p></dd>\n' % (
                date.strftime('%Y-%m-%d'), pandoc(description)))

    page.append('</dl>\n\n<p><ul>')
    if news['releases']:
        page.append('<li>')
        if len(news['releases']) == 1:
            page.append(_('One new release:'))
        else:
            page.append(_('{num_releases} new releases:').format(
                    num_releases=len(news['releases'])))
        page.append(' <a href="downloads">')
        first_items = itertools.islice(news['releases'].items(), 0, 4)
        page.append(', '.join('%s (%s)' % (trans_name(name), val[1])
                for name, val in first_items))
        if len(news['releases']) > 4:
            page.append(' %s…' % _("and more"))
        page.append('</a></li>\n')
    page.append('\n</ul>\n</p>\n')
    return common.HTML(''.join(page))

def file_current_enough(path):
    """Check whether the given file has been touched less than a minute ago."""
    if not os.path.exists(path):
        return False
    last_modified = datetime.fromtimestamp(os.path.getmtime(path))
    return last_modified  > (datetime.now() - timedelta(minutes=1))

def generate_news_section():
    """Retrieve news from multiple sources and generate a news section. If the
    environment variable DEBUG, databags/news.pickle is loaded, if it exists.
    Otherwise the file is retrieved and stored for subsequent debugging. If no
    internet access is present and no databags/news.pickle file exists, the news
    section will be empty."""
    news = None
    common.setup_gettext() # make localisation work
    if file_current_enough(DB_PICKLED):
        with open('databags/news.pickle', 'rb') as goodname:
            news = pickle.load(goodname)
    elif 'DEBUG' in os.environ:
        if not os.path.exists('databags/news.pickle'):
            return '' # no databag present, pretend empty news section
        with open('databags/news.pickle', 'rb') as goodname:
            news = pickle.load(goodname)
    else: # load fresh data
        timespan = timedelta(days=NEWS_TIMESPAN)

        news = {'releases': get_releases(timespan)}
        # load changelog entries from the last year and sort in ascending order
        news['changelog'] = collections.OrderedDict(sorted(((date, entry)
                for date, entry in common.load_changelog().items()
                if (datetime.now() - date) < timedelta(days=365)),
                reverse=True))
        if not os.path.exists('databags'):
            os.mkdir('databags')
        with open('databags/news.pickle', 'wb') as f:
            pickle.dump(news, f)
    return format_news(news)


