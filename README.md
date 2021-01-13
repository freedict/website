FreeDict.org
===========

This is the source code for the <https://freedict.org> web site.
If you find any mistakes, typos, etc., please
[tell us](https://freedict.org/community) or hand in a PR or patch.

We are looking for translators. It is not too much work and the website doesn't
change too often. So if you please a language other than listed on the bottom of
<https://freedict.org>, please consider translating the page for us.

Discussion takes place at our Wiki:

https://github.com/freedict/fd-dictionaries/wiki/Website-migration-to-Lektor

Website Translations
-----------------

We would appreciate your help for translating our website. It is not much work
and updates are minor. There are two ways to approach this:

1.  If  you are familiar with gettext, please hand in a PR. Add your language
    both in [freedict-org.lektorproject](freedict-org.lektorproject) and
    [configs/i18n.ini](configs/i18n.ini) and try to build using `lektor build`.
    If you cannot proceed, feel free to send us an
    [e-mail](https://www.freelists.org/list/freedict) and we'll sort
    things out for you.
2.  If you are not familiar with Gettext, please contact us on our
    [mailing list](https://www.freelists.org/list/freedict) and we will add the
    language for you. Afterwards, you will receive a ".po" file.

    Open the `.po`-file in a text editor. The first paragraph can be ignored.
    The subsequent paragraphs are the individual messages to be translated. The
    first line always starts with a hash `#`, please ignore this line and leave
    it unchanged. The next line contains the `msgid` with the actual message in
    quotes. This is the English text that serves as a basis for translation.
    Below is a line with `msgstr` and empty quotes. Insert the translation
    between the quotes.

    If you see  a longer translation like this:

    ````
    msgid ""
    "This is a long text that contains so little content that it is a hard task"
    "to extend over multiple lines."
    ```

    Your translation should be formatted the same way, especially, your
    translation should start with `msgstr ""` and the translation start on the
    next line.

    Any special characters, such as `%s` or `\n` need to be copied unchanged.
    Also, if possible, please limit the length of a line to 80 characters.

    Thanks already for your work! Please send the translated file back to us,
    e.g. via our [mailing list](https://www.freelists.org/list/freedict).
3.  Use a tool like [Poedit](https://poedit.net/download) that will aid in the
    translation process.

4.  A few strings don't need to be translated. Among these are the publications
    and code snippets.
Building
--------

This website generator depends on the following:

-   Python >= 3.4
-   gettext utilities
-   pybabel
-   Pandoc
-   Lektor; on Debian/Ubuntu use `apt install lektor` or `pip3 install lektor`
-   a fresh version of the FreeDict API
    -   if you happen to have the access rights, have a look at our wiki
        <https://github.com/freedict/fd-dictionaries/wiki/FreeDict-API> how to
        build the latest API and build it yourself.
    -   For everybody else: just download
        <https://freedict.org/freedict-database.json> and place it into the root
        directory of this project (the same as this README lies in).

### Building Locally

Invoking lektor build does require a internet connection to fetch items for the
"news" section. Setting the environment variable DEBUG (to any value) prevents
this. Building with a network connection, a file databags/news.pickle will be
created. Subsequent (DEBUG) runs will make use of this file, avoiding 403 by the
GitHub API.

### Building On The Server

Please see the head of `update_website` for document on the requirements, but in
general, it's enough to execute this script.

Extending
----------


All sites are written in markdown. Please only edit the contents.lr files,
because the contents+LANGCODE.lr files are auto-generated!

Also please do not use "------" for underlining headings, but instead "## TEXT",
because the plugin won't be able to handle dashed headings correctly.

Quirks
------

Some of these below are a repitition of what has been written below, but
sometimes it's better to have a separate section.

-   If you get errors from jinja telling you that `_` wasn't found, something
    went wrong with the Lektor cache. Do a friendly `rm -rf ~/.cache/lektor` and
    re-run.
-   Again, you need the FreeDict API files, namely the freedict-database.json in
    the root of this directory. If you are just testing the design, feel free to
    grab a copy from <https://freedict.org/freedict-database.json>
-   Please don't use dashed markdown headings:

        A Heading
        ---------

    These look very similar to a block delimiter in Lektor. Even though the
    lektor-i18n plugin tris not to interpret these, it might fail. Using `## A
    Heading` is safer.
