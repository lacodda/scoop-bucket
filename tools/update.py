#!/usr/bin/env python3
"""Write every manifest in bucket/ from packages.json and the newest release.

One package is one entry in packages.json: the GitHub repository it is
released from, how it describes itself, the program and its aliases. The
manifest is never edited by hand - the next run would write over it - so a
change goes into packages.json or into this script.

For each package the newest GitHub release is read, its Windows x86-64 archive
is downloaded and hashed, and bucket/<name>.json is rendered with Scoop's own
checkver and autoupdate, so Scoop's tools can follow it too. Run with no
arguments; GITHUB_TOKEN, when set, lifts the API's rate limit.
"""

import hashlib
import json
import os
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGET = "x86_64-pc-windows-msvc"


def fetch(url, accept="application/octet-stream"):
    headers = {"User-Agent": "lacodda-scoop-bucket", "Accept": accept}
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=120) as reply:
        return reply.read()


def latest(repo):
    release = json.loads(fetch(f"https://api.github.com/repos/{repo}/releases/latest", "application/vnd.github+json"))
    return release["tag_name"], {asset["name"]: asset["browser_download_url"] for asset in release["assets"]}


def render(package, tag, assets):
    name, version, repo = package["name"], tag.removeprefix("v"), package["repo"]
    archive = f"{name}-{tag}-{TARGET}.zip"
    if archive not in assets:
        sys.exit(f"{repo} {tag} carries no {archive}")
    exe = f"{package['bin']}.exe"
    # Each alias is a shim of its own name that runs the same binary.
    bins = [exe] + [[exe, alias] for alias in package.get("aliases", [])]
    manifest = {
        "version": version,
        "description": package["desc"],
        "homepage": package["homepage"],
        "license": package["license"],
        "architecture": {
            "64bit": {
                "url": assets[archive],
                "hash": hashlib.sha256(fetch(assets[archive])).hexdigest(),
                "extract_dir": f"{name}-{tag}-{TARGET}",
            }
        },
        "bin": bins,
        "checkver": {"github": f"https://github.com/{repo}"},
        "autoupdate": {
            "architecture": {
                "64bit": {
                    "url": f"https://github.com/{repo}/releases/download/v$version/{name}-v$version-{TARGET}.zip",
                    "extract_dir": f"{name}-v$version-{TARGET}",
                }
            }
        },
    }
    return json.dumps(manifest, indent=4) + "\n"


def main():
    packages = json.loads((ROOT / "packages.json").read_text(encoding="utf-8"))
    changed = []
    for package in packages:
        tag, assets = latest(package["repo"])
        manifest = ROOT / "bucket" / f"{package['name']}.json"
        text = render(package, tag, assets)
        if not manifest.exists() or manifest.read_text(encoding="utf-8") != text:
            manifest.write_text(text, encoding="utf-8", newline="\n")
            changed.append(f"{package['name']} {tag}")
    print("updated: " + ", ".join(changed) if changed else "every manifest is on its newest release")
    summary = os.environ.get("GITHUB_OUTPUT")
    if summary:
        with open(summary, "a", encoding="utf-8") as out:
            out.write(f"changed={'; '.join(changed)}\n")


if __name__ == "__main__":
    main()
