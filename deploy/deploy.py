import argparse
from os.path import join
import os
import sys
import json
import tempfile
import getpass
import requests
from paramiko.client import SSHClient, AutoAddPolicy
from twine.commands.upload import main as twine_upload


def fetch(path):
    r = requests.get("https://api.github.com" + path)
    return json.loads(r.text)


def get_asset_urls(package, version=None):
    rel_name = "latest" if version is None else f"tags/v{version}"
    release = fetch(f"/repos/biotite-dev/{package}/releases/{rel_name}")
    if "message" in release and release["message"] == "Not Found":
        raise ValueError(
            f"Release '{rel_name}' is not existing"
        )
    assets = {}
    for asset in release["assets"]:
        assets[asset["name"]] = asset["browser_download_url"]
    return assets


def remote_exec(client, command):
    print(command)
    stdin, stdout, stderr = client.exec_command(command)
    stdout_str = stdout.read().decode("utf-8").strip()
    stderr_str = stderr.read().decode("utf-8").strip()
    if stdout_str:
        print(stdout_str)
    if stderr_str:
        print("ERROR: " + stderr_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload a Package release on GitHub to PyPI"
                    "and deploy the documentation on the documentation "
                    "website host server"
    )
    parser.add_argument(
        "--version", "-v", dest="version",
        help="Version to be distributed (latest by default)")
    parser.add_argument(
        "--package", "-p", dest="package", default="biotite",
        help="Name of the project to be distributed")
    args = parser.parse_args()
    
    temp_dir = tempfile.gettempdir()
    dist_dir = join(temp_dir, "dist")
    os.mkdir(dist_dir)
    print("Download release assets...")
    doc_url=None
    for name, url in get_asset_urls(args.package, args.version).items():
        if name.startswith(args.package):
            # Distribution file (.whl or .tar.gz)
            r = requests.get(url)
            fname = join(dist_dir, name)
            with open(fname, "wb") as file:
                file.write(r.content)
        elif name == "doc.zip":
            # Documentation file
            doc_url = url
        else:
            raise ValueError(f"Unknown asset '{name}'")
    if doc_url is None:
        raise ValueError("Release has no documentation")


    # Upload distributions to PyPI
    print("Upload distributions to PyPI...")
    twine_upload([f"{dist_dir}/*"])


    # Upload documentation on host server
    print("Upload documentation to host server...")
    hostname = input("Hostname: ")
    username = input("Username: ")
    password = getpass.getpass()
    html_dir = f"./{args.package}"

    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy)
    client.connect(hostname=hostname, username=username, password=password)

    # Naviagte into home directory
    remote_exec(client, f"cd /home/{username}")
    # Download zipped documentation into home directory
    remote_exec(client, f"wget -q {doc_url}")
    # Remove currently published documentation
    remote_exec(client, f"rm -rf {html_dir}/*")
    # Make sure that the directory we unpack to is not existing
    remote_exec(client, f"rm -rf doc")
    # Unpack documentation
    remote_exec(client, f"unzip -q doc.zip")
    # Publish documentation
    remote_exec(client, f"mv doc/* {html_dir}")
    # Remove intermediate files
    remote_exec(client, f"rm -r doc")
    remote_exec(client, f"rm doc.zip")

    client.close()
