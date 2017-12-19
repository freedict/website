import gettext
import json
import os
import re
import subprocess
import sys
import urllib.request

from lektor.pluginsystem import Plugin
from lektor.context import get_ctx

_ = None

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

    def on_process_template_context(self, context, **extra):
        def test_function():
            return 'Value from plugin %s' % self.name
        context['test_function'] = test_function

    def on_setup_env(self, **extra):
        self.env.jinja_env.globals.update(generate_download_section=
                generate_download_section)



def load_iso_table():
    if not os.path.exists('iso-639-3.tab'):
        with urllib.request.urlopen('http://www-01.sil.org/iso639-3/iso-639-3.tab') as u:
            with open('iso-639-3.tab', 'wb') as f:
                f.write(u.read())
    with open('iso-639-3.tab', encoding='UTF-8') as f:
        return {line.split('\t')[0]:
            re.sub(r'\\s+\(.*?\)$', '', line.split('\t')[-2]) for line in
            f.read().split('\n')}

def code2name(isotable, name):
    lg1, lg2 = name.split('-')
    return '%s - %s' % (isotable[lg1], isotable[lg2])


def mkpage(dictionaries, codes):
    languages = {l for k in dictionaries for l in k.split('-')}
    # ToDo: language names are not localised
    _ = lambda x: x
    page = ['\n\n', _('Pick a language:'), ('\n\n<select onchange="'
        'showDictionaries(this);">\n<option value="none">'),
        _('Select a language…</option>')]
    page.append('\n'.join('<option value="%s">%s</option>' % (l, codes[l])
        for l in sorted(languages, key=lambda l: codes[l])))
    page.append('</select>\n\n')

    # ToDo: locale sorting
    for name, info in sorted(dictionaries.items()):
        lg1, lg2 = name.split('-')
        page.append('\n<li class="dict-entry dict-src-%s ' % lg1)
        page.append('dict-trg-%s" style="display: none">' % lg2)
        page.append('<a href="%s">%s - %s</a></li>\n' % (info['URL'], _(codes[lg1]),
            _(codes[lg2])))
    return ''.join(page)

def generate_download_section(target):
    """Target is either 'mobile' or 'desktop'."""
    global _
    ctx = get_ctx()
    try:
        translator = gettext.translation("contents",
            os.path.join('i18n', '_compiled'), languages=[ctx.locale], fallback = True)
    except AttributeError:
        print("No locale found, assuming English.")
        translator = gettext.translation("contents",
            os.path.join('i18n', '_compiled'), languages=['en'], fallback = True)

    gettext.bindtextdomain('freedict', os.path.join('i18n', '_compiled'))
    _ = translator.gettext

    json_api = load_json_api()
    codes = load_iso_table()
    dictionaries = {}
    for dictionary in json_api:
        try:
            slob = next(r for r in dictionary['releases'] if r['platform'] == 'slob')
        except StopIteration:
            raise ValueError("Dictionary %s without slob" % dictionary['name'])
        name = dictionary['name']
        dictionaries[name] = slob
    return mkpage(dictionaries, codes)

if __name__ == '__main__':
    generate_download_section('mobile')

