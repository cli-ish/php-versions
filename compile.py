import json
import re
import urllib.request
from datetime import datetime

section_re = r"<section .*?>(.*?)<\/section>"


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def load_php_releases():
    result = {}
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December']

    contents = urllib.request.urlopen("https://www.php.net/releases/").read().decode()
    matches = re.findall(section_re, contents, re.DOTALL)
    if len(matches) != 1:
        return []
    versions_re = r"<h2>(.*?)</h2>.*?<li>Released: (.*?)<\/li>"
    raw_versions = re.findall(versions_re, matches[0], re.DOTALL)
    for version in raw_versions:
        release, release_date = version
        for month in months:
            release_date = release_date.replace(month, month[0:3])
        d = datetime.strptime(release_date, '%d %b %Y')
        result[release] = {'release': release, 'date': d.strftime('%d.%m.%Y')}
    return result


def mark_last_version(versions):
    sorted_list = list(versions.keys())
    sorted_list.sort(key=natural_keys)
    for i in range(0, len(sorted_list)):
        version = sorted_list[i]
        parts = version.split(".")
        if len(parts) != 3:
            continue  # ignore weird versions?
        crafted_version = parts[0] + "." + parts[1] + "."
        if i + 1 > len(sorted_list) - 1:
            versions[version]['last'] = True
            break
        if not sorted_list[i + 1].startswith(crafted_version):
            versions[version]['last'] = True


def mark_eol_versions(versions):
    contents = urllib.request.urlopen("https://www.php.net/eol.php").read().decode()
    matches = re.findall(section_re, contents, re.DOTALL)
    if len(matches) != 1:
        return
    versions_re = r"<td>(\d+.\d+)<\/td>"
    raw_versions = re.findall(versions_re, matches[0], re.DOTALL)
    for version_old in raw_versions:
        for version in versions.keys():
            if version.startswith(version_old + "."):
                versions[version]['eol'] = True


def main():
    versions = load_php_releases()
    mark_last_version(versions)
    mark_eol_versions(versions)
    with open("./data/versions.json", "w") as f:
        json.dump(versions, f, sort_keys=True, indent=4)
    print(versions)


if __name__ == '__main__':
    main()
