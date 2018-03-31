"""Tis module contains common functions and classes to load external resources
or to interact with them."""

import collections
import datetime
import json
import gettext
import os
import re
import urllib
import yaml

from lektor.context import get_ctx

def load_json_api():
    """This function returns the JSON representation of the FreeDict API. It
    requires the a freedict.jsonin the top-level of this project. Have a look at
    `make api` from the FreeDict tools or fetch a copy from
    https://freedict.org/freedict-database.json."""
    try:
        with open('freedict-database.json') as greatvarname:
            return json.load(greatvarname)
    except FileNotFoundError:
        raise FileNotFoundError(("Couldn't find a freedict-database.json in "
                "the top level of this project. Please have a look at the "
                "README how to get one."))


def load_iso_table():
    """Load the table of iso-639-3 language code to English name mappings,
    retrieve from the web if missing."""
    if not os.path.exists('iso-639-3.tab'):
        with urllib.request.urlopen('http://www-01.sil.org/iso639-3/iso-639-3.tab') as u:
            with open('iso-639-3.tab', 'wb') as f:
                f.write(u.read())
    with open('iso-639-3.tab', encoding='UTF-8') as f:
        # preserve order to avoid changing the *.po files over and over again
        codes = collections.OrderedDict()
        strip_paren = lambda x: re.sub(r'(.*?)\s*\(.*\)$', r'\1', x).strip()
        for line in f.read().split('\n'):
            codes[line.split('\t')[0]] = strip_paren(line.split('\t')[-2])
        return codes

def load_changelog():
    """This function returns a simple mapping from datetime object to (textual)
    changelog entry."""
    # we assume to be in the lektor project root
    if not os.path.exists('Changelog'):
        return {}
    with open('Changelog') as f:
        # order entries, convert datetime.date to datetime.datetime
        d2d = lambda d: datetime.datetime(year=d.year, month=d.month, day=d.day)
        return collections.OrderedDict(sorted(((d2d(k), v)
            for k,v in yaml.load(f).items()), reverse=True))


def setup_gettext():
    """Retrieve locale from lektor settings and install the _ function to do its
    work."""
    ctx = get_ctx()
    try:
        translator = gettext.translation("contents",
            os.path.join('i18n', '_compiled'), languages=[ctx.locale], fallback = True)
        translator.install()
    except AttributeError:
        print("No locale found, assuming English.")
        translator = gettext.translation("contents",
            os.path.join('i18n', '_compiled'), languages=['en'], fallback = True)
        translator.install()


class HTML():
    """A simple wrapper which instructs lektor to not escape HTML tags in the
    resulting file."""
    def __init__(self, html):
        self.html = html

    def __html__(self):
        return self.html



