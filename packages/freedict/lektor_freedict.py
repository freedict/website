import collections
import datetime
import os
import re
import tempfile
import time

from lektor.pluginsystem import Plugin
from lektor.utils import portable_popen

import news
from common import HTML, load_json_api, load_iso_table, setup_gettext

#pylint: disable=too-few-public-methods
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
        # add all functions which should be visible from the jinja2 templates
        self.env.jinja_env.globals.update(
                get_year = get_year,
                generate_download_section = generate_download_section,
                generate_maintainer_overview = generate_maintainer_overview,
                generate_news_section=news.generate_news_section)
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
        # retrieve relative path from lektor project root
        directory = os.path.dirname(os.path.abspath(__file__))
        directory = directory.replace(os.getcwd() + os.sep, '')
        pyfiles = [os.path.join(directory, f) for f in os.listdir(directory)
                if f.endswith('.py')]
        xgettext = portable_popen(['xgettext', '-L', 'Python',
            '--from-code=UTF-8', '-o', plugin_pot.name] + pyfiles)
        ret = xgettext.wait()
        if ret:
            raise OSError('xgettext exited with %d' % ret)
        with open(os.path.join('i18n', 'plugins.pot'), 'wb') as f:
            portable_popen(['msgcat', "--use-first", lang_pot.name, '-t',
                    'UTF-8', plugin_pot.name], stdout=f).wait()


def mk_dropdown(dictionaries, codes, platform):
    """This function generates the drop-down menu on the downloads page to
    select the available languages."""
    languages = {l for k in dictionaries for l in k.split('-')}
    languages = collections.OrderedDict(sorted(((l, _(codes[l]))
        for l in languages), key=lambda x: _(x[1])))
    page = ['\n\n<p><label>', _('Pick a language:'), '\n\n<select onchange="'
        'showDictionaries(this, \'%s\');">\n<option value="none">' % platform,
        _('No language selected…'), '</option>']
    page.append('\n'.join('<option value="%s">%s</option>' % (code, name)
        for code, name in languages.items()))
    page.append('</select></label></p><hr/>\n\n<p><ul>')

    for abbr_name, dictionary in dictionaries.items():
        lg1, lg2 = abbr_name.split('-')
        page.append('\n<li style="list-style-type:circle; display: none" class="dict-src-%s ' % lg1)
        page.append('dict-trg-%s %s">' % (lg2, platform))
        page.append('<a href="%s">%s, ' % (dictionary['url'],
                dictionary['localised_name']))
        page.append(_('version {version} with {headwords} headwords').format(
                version=dictionary['edition'], headwords=dictionary['headwords']))
        page.append('</a></li>\n')
    page.append('\n</ul></p>\n')
    return ''.join(page)

def generate_download_section(target):
    """Target can be either 'mobile' or 'desktop'."""
    if not target in ('mobile', 'desktop'):
        raise ValueError("Expected either mobile or desktop as target, got " + \
                repr(target))

    setup_gettext()
    json_api = load_json_api()
    codes = load_iso_table()
    dictionaries = {}
    trans_name = lambda n: '%s - %s' % (_(codes[n.split('-')[0]]),
            _(codes[n.split('-')[1]]))
    platform = ('slob' if target == 'mobile' else 'dictd')
    for dictionary in json_api:
        try:
            url = next(r for r in dictionary['releases'] if r['platform'] ==
                    platform)['URL']
        except StopIteration:
            raise ValueError("Dictionary %s without release for %s" % (
                dictionary['name'], platform))
        name = dictionary['name']
        dictionaries[name] = {'url': url, 'edition': dictionary['edition'],
                'headwords': dictionary['headwords'],
                'localised_name': trans_name(name)}
    # sort dictionaries with locale-specific naming
    dictionaries = collections.OrderedDict(sorted(dictionaries.items(),
            key=lambda entry: entry[1]['localised_name']))
    return HTML(mk_dropdown(dictionaries, codes, target))

def get_year():
    return str(datetime.datetime.now().year)

def generate_maintainer_overview():
    """Generate a maintainer section for the community page."""
    setup_gettext()
    maint2dicts = {}
    languages = {id: _(name) for id, name in load_iso_table().items()}
    def trans_name(name):
        lg1, lg2 = name.split('-') # ISO 639-3 xxx-yyy naming
        return '%s - %s' % (languages[lg1], languages[lg2])

    for dictionary in load_json_api():
        if "maintainerName" not in dictionary or 'no maint' in \
                dictionary['maintainerName']:
            continue
        name = dictionary['maintainerName']
        if not name in maint2dicts:
            maint2dicts[name] = []
        maint2dicts[name].append(trans_name(dictionary['name']))
    return collections.OrderedDict(sorted(maint2dicts.items()))

if __name__ == '__main__':
    print(generate_maintainer_overview())
