"""Tis module contains functions to load external resources, required for
generating information on the freedict.org web site."""

import collections
import datetime
import json
import os
import re
import subprocess
import sys
import urllib
import yaml

def load_json_api():
    """This function returns the JSON representation of the FreeDict API. It
    requires the environment variable FREEDICT_TOOLS  to be set and a FreeDict
    configuration with a valid API output path, try
    `make -C $FREEDICT_TOOLS api-path`
    as a test."""
    if not 'FREEDICT_TOOLS' in os.environ:
        raise OSError('The environment variable has to be set.')
    proc = subprocess.Popen(['make', '--no-print-directory', '-C',
        os.environ['FREEDICT_TOOLS'], 'api-path'], stdout=subprocess.PIPE)
    ret = proc.wait()
    if ret:
        raise OSError(("Failed to execute `make -C $FREEDICT_TOOLS api-path`, "
            "process exited with error code %d") % ret)
    path = os.path.join(proc.communicate()[0].decode(sys.getdefaultencoding()),
        'freedict-database.json')
    return json.load(open(path))


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



