from setuptools import setup

setup(
    name='lektor-freedict',
    version='0.1',
    author=u'Sebastian Humenda,,,',
    author_email='shumenda@gmx.de',
    license='MIT',
    py_modules=['lektor_freedict'],
    entry_points={
        'lektor.plugins': [
            'freedict = lektor_freedict:FreedictPlugin',
        ]
    }
)
