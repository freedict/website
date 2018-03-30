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
    -   if you happen to have the access rights, have a look at our wiki
        <https://github.com/freedict/fd-dictionaries/wiki/FreeDict-API> how to
        build the latest API and build it yourself.
    -   For everybody else: just download
        <https://freedict.org/freedict-database.json> and place it into the root
        directory of this project (the same as this README lies in).

Invoking lektor build does require a internet connection to fetch items for the
"news" section. Setting the environment variable DEBUG (to any value) prevents
this. Building with a network connection, a file databags/news.pickle will be
created. Subsequent (DEBUG) runs will make use of this file, avoiding 403 by the
GitHub API.

