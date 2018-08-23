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

Building
--------

This website generator depends on the following:

-   Python >= 3.4
-   gettext utilities
-   pybabel
-   Pandoc
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

