# Chrome Search Engine Importer

Custom Search Engines in chrome can make searching for things in private/internal systems a lot more efficient and easier, so long as those systems allow you to input the search string in the URI.

Custom Search Engines can also function as keyword shortcuts to URLs, if you don't wish to fumble around with your bookmarks and would rather type in a keyword in the search bar + <Enter> to take you to where you are trying to go.

However, when you collaborate with other people who often use the same systems that you do, it can be helpful to share these custom search gines with one another. The [manual method](https://zapier.com/blog/add-search-engine-to-chrome/) for adding custom search engines does not scale well when you need to share a lot of them. Thus, the need for this script to make that manual process easier and the framework of defining custom search engine keywords as YAML files.

# How does it work?

## Defining search engine keywords in YAML

You will need to create a YML file with your hsortcuts like the example below. The example file, `example_search_engines.yml` also has some practical examples.

```
- name: Shortcut 1 Name
  keyword: shorcut1keyword
  url: https://shortcut1/url?q={searchTerms}
- name: Shortcut 2 Name
  keyword: shortcut2keyword
  url: https://shortcut2url.com/search/%s
- name: Virustotal UI
  keyword: vtui
  url: https://www.virustotal.com
```

NOTE: `%s` and `{searchTerms}` are synonymous. All occurrences of `%s` in the URL are replaced with `{searchTerms}` when being added to the database.

## Using the script

Once you have defined your shortcuts, you may use the script, you must pass the path to the YML file to it. Example:

`python3 chrome-search-engine-importer.py -e example_search_engines.yml`

By default, the script will look in the default paths for Chrome profiles (on MacOS, Windows, and Linux). You will be given the option to choose which profiles found in the default paths to load the keyhwords in.

To bypass this, you may optionally use the `-p` flag to specify a path to a profile that is not in a default path.  
_NOTE: The path should point to the directory that has the sqlite database file `Web Data` inside of it._

```
> python3 chrome-search-engine-importer.py --help
Usage: chrome-search-engine-importer.py [OPTIONS]

Options:
  -e, --search-engines-file TEXT  Path to a YAML file with search engines
                                  defined  [required]
  -p, --profile TEXT              Path to a chrome profile. Useful if a target
                                  chrome profile is in a custom path.
  --help                          Show this message and exit.
```

The script will install any keywords in the YAML that do not already exist in the `Web Data` database. If you want to add these to be added, either adjust modify the keyword so that it is unique, or delete the existing keyword from your chrome search engines [here](chrome://settings/searchEngines).

### You have to restart chrome

_On Windows, Chrome needs to be closed while the script runs_ otherwise you will encounter an error when the script tries to swap out the Web Data sqlite database.

For the newly added keywords to be visible in chrome, you must relaunch Chrome so that it reloads the SQLite database. I recommend enabling the "Continue where you left off" [Startup Option](chrome://settings/onStartup) in Chrome so that your tabs recover after you restart the browser.
