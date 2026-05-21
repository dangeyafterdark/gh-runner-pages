# static site in markdown for tracking runner image changes
#
# parse runner-images repo readme and releases/tags to detect changes

import re
from pathlib import Path

import requests

image_os = ["ubuntu", "windows", "macOS"]


def request(path):
    url = "https://raw.githubusercontent.com/actions/runner-images/main" + path
    res = requests.get(url)

    if res.status_code != 200:
        raise Exception(f"Failed to retrieve file: {res.status_code}")

    return res.text


def parse_labels_links(text):
    start = text.find("## Label scheme")
    end = text.find("[self-hosted runners]")

    if start < 0 or end < 0:
        raise Exception(
            f"Error parsing substring: start index: {start} - end index: {end}"
        )

    text = text[start : (end - 1)]
    text = text[text.find("[ubuntu") :]

    labels = {}

    for os in image_os:
        labels[os] = re.findall(rf"\[{os}-[\w.-]+\]", text)

    links = re.findall(r"/images/[\w.-]+/[\w.-]+", text)

    return labels, links


def generate_md_file(labels, links):
    text = ""
    i = 0
    with open("page.md", "w") as f:
        f.write("## GitHub-hosted Runner Images\n")
        f.write("\n")
        for os in labels.keys():
            f.write(f"### {os}\n")
            for label in labels[os]:
                f.write(f"- {label}\n")

                text += f"{label}: {links[i]}\n"
                i += 1

        f.write("\n")
        f.write(text)

    return


def generate_tools_md(links):
    for link in links:
        filepath = Path(f".{link}")
        filepath.parent.mkdir(parents=True, exist_ok=True)

        text = request(link)
        text = text[text.find("***") :]

        with filepath.open("w", encoding="utf-8") as f:
            f.write(text)

    return


def main():
    try:
        text = request("/README.md")
        labels, links = parse_labels_links(text)
        generate_md_file(labels, links)
        generate_tools_md(links)

    except Exception as err:
        print(err)


main()
