This is the source code for the <https://freedict.org> web site, which is NOT
YET deployed. Your are welcome to help out

Discussion takes place at our Wiki:

https://github.com/freedict/fd-dictionaries/wiki/Website-migration-to-Lektor

Building
--------

This website generator depends on the following:

-   Python >= 3.4
-   gettext utilities
-   pybabel
-   a fresh version of the FreeDict API
    -   if you want (and can) build yourself, check out
        <https://github.com/freedict/fd-dictionaries/wiki/FreeDict-API>.
    -   If you are only interested in improving the website, here's what you
        need to do:
        -   Clone <https://github.com/freedict/tools> (if not done already) and
            set the environment variable `FREEDICT_TOOLS` to point to this
            directory.
        -   Initialise a configuration like explained on
            <https://github.com/freedict/fd-dictionaries/wiki/FreeDict-HOWTO-%E2%80%93-FreeDict-Build-System>,
            most important is the `api_output_path`
        -   Fetch <https://freedict.org/freedict-database.json> and save it to
            the directory configured above.

Invoking lektor build does require a internet connection to fetch items for the
"news" section. Setting the environment variable DEBUG (to any value) prevents
this. Building with a network connection, a file databags/news.pickle will be
created. Subsequent (DEBUG) runs will make use of this file, avoiding 403 by the
GitHub API.

