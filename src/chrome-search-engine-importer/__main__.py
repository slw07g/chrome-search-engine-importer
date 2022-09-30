import logging
import os
import sqlite3
import sys
import shutil
import click
import inquirer
import yaml

logging.getLogger().setLevel(logging.INFO)

# Default paths for where chrome profiles can be found as subdirectories.
DEFAULT_CHROME_PATHS = {
    'darwin': ['~/Library/Application Support/Google/Chrome/'],
    'win32': ['%USERPROFILE%\\AppData\\Local\\Google\\Chrome\\User Data'],
    'linux': ['~/.config/google-chrome/']
}

TMP_WEB_DATA_PATH = os.path.join('%USERPROFILE%',
                                 '.tmp_web_data') if sys.platform == 'win32' else os.path.join(
                                     '~', '.tmp_web_data')


def copy_file(src: str, dst: str) -> None:
    logging.info("Copying %s to %s", src, dst)
    shutil.copyfile(expand_path(src), expand_path(dst))


def rm_file(path: str) -> None:
    logging.info("Deleting %ss", path)
    os.remove(expand_path(path))


def expand_path(path: str) -> str:
    return os.path.abspath(os.path.normpath(os.path.expanduser(os.path.expandvars(path))))


def check_keyword_exists(con: sqlite3.Cursor, keyword: str) -> bool:
    cursor = con.execute('SELECT * FROM keywords WHERE keyword = ?', [keyword])
    results = cursor.fetchall()
    return len(results) > 0


def install_search_engines(target: str, engines: list = None) -> bool:
    print(engines)
    web_data_original = os.path.join(target, 'Web Data')
    copy_file(web_data_original, TMP_WEB_DATA_PATH)
    con = sqlite3.connect(expand_path(TMP_WEB_DATA_PATH))
    profile_name = os.path.basename(target)

    for engine in engines:
        keyword = engine['keyword']
        name = engine['name']
        url = engine['url']
        if not check_keyword_exists(con, engine['keyword']):
            logging.info(
                'Adding keyword [%s] to profile [%s]',
                keyword,
                profile_name,
            )
            con.execute(
                'INSERT INTO keywords(short_name, keyword, url, favicon_url) values (?, ?, ?, "");',
                [name, keyword, url.replace('%s', '{searchTerms}')])
            con.commit()
        else:
            logging.info(
                'Keyword [%s] already exists in profile [%s]...skipping...',
                keyword,
                profile_name,
            )
    con.close()
    copy_file(TMP_WEB_DATA_PATH, web_data_original)
    rm_file(TMP_WEB_DATA_PATH)


def read_search_engines(path: str) -> list:
    logging.info("Loading search engines from %s", path)
    return yaml.safe_load(open(expand_path(path), 'rb'))


def get_chrome_profile_paths() -> list:
    profile_paths = []
    logging.info('Searching for chrome profiles in default paths')
    for path in DEFAULT_CHROME_PATHS.get(sys.platform, []):
        for root, _, _ in os.walk(expand_path(path)):
            if os.path.exists(os.path.join(
                    root, 'Web Data')) and os.path.basename(root) != 'System Profile':
                profile_paths.append(root)
            continue
    return profile_paths


def get_target_profiles(profile_paths: list) -> list:
    prompts = [
        inquirer.Checkbox(
            'profiles',
            message="Which Chrome profiles should the search engines be installed on? (You may select more than one)",
            choices=profile_paths,
            default=profile_paths[0] if len(profile_paths) > 0 else None),
    ]

    answers = inquirer.prompt(prompts)
    return answers.get('profiles', [])


@click.command()
@click.option(
    '--search-engines-file',
    '-e',
    help="Path to a YAML file with search engines defined",
    type=str,
    required=True)
@click.option(
    '--profile',
    '-p',
    help="Path to a chrome profile. Useful if a target chrome profile is in a custom path.",
    type=str,
    required=False)
def main(search_engines_file: str = None, profile: str = None):
    profile_paths = get_chrome_profile_paths() if not profile else profile.split(',')
    targets = get_target_profiles(profile_paths)
    engines = read_search_engines(search_engines_file)
    for target in targets:
        print(target)
        install_search_engines(target, engines=engines)


if __name__ == '__main__':
    main()