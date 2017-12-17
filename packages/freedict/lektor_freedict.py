from lektor.pluginsystem import Plugin


class FreedictPlugin(Plugin):
    name = 'freedict'
    description = 'FreeDict page generator functionality'

    def on_process_template_context(self, context, **extra):
        def test_function():
            return 'Value from plugin %s' % self.name
        context['test_function'] = test_function
