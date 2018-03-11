import datetime
import gettext
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.request

from lektor.context import get_ctx
from lektor.pluginsystem import Plugin
from lektor.utils import portable_popen

class HTML():
    """A simple wrapper which instructs lektor to not escape HTML tags in the
    resulting file."""
    def __init__(self, html):
        self.html = html

    def __html__(self):
        return self.html


def load_json_api():
    """This function returns the JSON representation of the FreeDict API. It
    requires environment variable FREEDICT_TOOLS  to be set and a FreeDict
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


class FreedictPlugin(Plugin):
    name = 'freedict'
    description = 'FreeDict page generator functionality'

    def get_used_languages(self):
        """Parse ISO language codes and FreeDict API file and compile a list of
        all existing (English) language names."""
        table = load_iso_table()
        # dictionaries are named like "lg1-lg2", split strng and query English
        # name
        dictionaries = (d['name'] for d in load_json_api())
        # compile list of unique ISO codes
        codes = set(code for dummy in (keys.split('-') for keys in dictionaries)
                for code in dummy)
        return [table[code] for code in codes]


    #pylint: disable=unused-argument
    def on_setup_env(self, **extra):
        self.env.jinja_env.globals.update(generate_download_section=
                generate_download_section)
        # craft temporary POT file with languages
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        now += '+%s'%(time.tzname[0])
        pot = [re.sub('\n\\s+', '\n', """msgid ""\nmsgstr ""\n
                "Project-Id-Version: 0.0.0\\n"
                "Report-Msgid-Bugs-To: freedict@freelists.org\\n"
                "POT-Creation-Date: {}s\\n"\n "PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
                "Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
                "Language-Team: FreeDict <freedict@freelists.org>\\n"
                "Language: LANGUAGE\\n"
                "MIME-Version: 1.0\\n"\n"Content-Type: text/plain; charset=UTF-8\\n"
                "Content-Transfer-Encoding: 8bit\\n"\n""".format(now))]
        for lang in self.get_used_languages():
            pot.append('\n#: iso-639-3.tab (no:lineno)\n')
            pot.append('msgid "{}"\nmsgstr ""\n'.format(lang))
        if not os.path.exists("i18n"):
            os.mkdir("i18n")
        lang_pot = tempfile.NamedTemporaryFile(suffix='pot')
        lang_pot.write(''.join(pot).encode('UTF-8'))
        lang_pot.flush()
        plugin_pot = tempfile.NamedTemporaryFile(suffix='pot')
        xgettext = portable_popen(['xgettext', '-L', 'Python',
            '--from-code=UTF-8', os.path.relpath(__file__), '-o',
            plugin_pot.name])
        xgettext.wait()
        with open(os.path.join('i18n', 'plugins.pot'), 'wb') as f:
            portable_popen(['msgcat', "--use-first", lang_pot.name, '-t',
                    'UTF-8', plugin_pot.name], stdout=f).wait()


def load_iso_table():
    if not os.path.exists('iso-639-3.tab'):
        with urllib.request.urlopen('http://www-01.sil.org/iso639-3/iso-639-3.tab') as u:
            with open('iso-639-3.tab', 'wb') as f:
                f.write(u.read())
    with open('iso-639-3.tab', encoding='UTF-8') as f:
        codes = {}
        strip_paren = lambda x: re.sub(r'(.*?)\s*\(.*\)$', r'\1', x).strip()
        for line in f.read().split('\n'):
            codes[line.split('\t')[0]] = strip_paren(line.split('\t')[-2])
        return codes

def code2name(isotable, name):
    lg1, lg2 = name.split('-')
    return '%s - %s' % (isotable[lg1], isotable[lg2])


def mk_dropdown(dictionaries, codes, platform):
    languages = {_(l) for k in dictionaries for l in k.split('-')}
    page = ['\n\n<p><label>', _('Pick a language:'), '\n\n<select onchange="'
        'showDictionaries(this, \'%s\');">\n<option value="none">' % platform,
        _('No language selected…'), '</option>']
    page.append('\n'.join('<option value="%s">%s</option>' % (l, codes[l])
        for l in sorted(languages, key=lambda l: codes[l])))
    page.append('</select></label></p><hr/>\n\n<ul>')

    # sort dictionaries by local name
    localised_names = {'%s - %s' % \
             (_(codes[k.split('-')[0]]), _(codes[k.split('-')[1]])):
             k for k in dictionaries}
    for name, code in sorted(localised_names.items()):
        lg1, lg2 = code.split('-')
        page.append('\n<li class="dict-src-%s ' % lg1)
        page.append('dict-trg-%s %s" style="display: none">' % (lg2, platform))
        page.append('<a href="%s">%s</a></li>\n' % \
                (dictionaries[code]['URL'], _(name)))
    page.append('\n</ul>\n')
    return ''.join(page)

def generate_download_section(target):
    """Target can be either 'mobile' or 'desktop'."""
    if not target in ('mobile', 'desktop'):
        raise ValueError("Expected either mobile or desktop as target, got " + \
                repr(target))
    ctx = get_ctx()
    try:
        translator = gettext.translation("contents",
            os.path.join('i18n', '_compiled'), languages=[ctx.locale], fallback = True)
        translator.install()
    except AttributeError:
        print("No locale found, assuming English.")
        translator = gettext.translation("contents",
            os.path.join('i18n', '_compiled'), languages=['en'], fallback = True)

    json_api = load_json_api()
    codes = load_iso_table()
    dictionaries = {}
    platform = ('slob' if target == 'mobile' else 'dictd')
    for dictionary in json_api:
        try:
            url = next(r for r in dictionary['releases'] if r['platform'] ==
                    platform)
        except StopIteration:
            raise ValueError("Dictionary %s without release for %s" % (
                dictionary['name'], platform))
        name = dictionary['name']
        dictionaries[name] = url
    return HTML(mk_dropdown(dictionaries, codes, target))

if __name__ == '__main__':
    generate_download_section('mobile')

