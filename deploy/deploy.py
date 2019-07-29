import argparse
from os.path import join
import os
import sys
import json
import getpass
import biotite
import requests
from paramiko.client import SSHClient, AutoAddPolicy
from twine.commands.upload import main as twine_upload


def fetch(path):
    r = requests.get("https://api.github.com" + path)
    return json.loads(r.text)


def get_asset_urls(version=None):
    rel_name = "latest" if version is None else f"tags/v{version}"
    release = fetch(f"/repos/biotite-dev/biotite/releases/{rel_name}")
    if "message" in release and release["message"] == "Not Found":
        raise ValueError(f"Release 'v{version}' is not existing")
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
        description="Upload a Biotite release on GitHub to PyPI"
                    "and deploy the documentation on the Biotite website"
                    "host server"
    )
    parser.add_argument(
        "--version", "-v", dest="version",
        help="Biotite version to be distributed (latest by default)")
    args = parser.parse_args()
    
    temp_dir = biotite.temp_dir()
    dist_dir = join(temp_dir, "dist")
    os.mkdir(dist_dir)
    print("Download release assets...")
    for name, url in get_asset_urls(args.version).items():
        if name.startswith("biotite"):
            # Distribution file (.whl or .tar.gz)
            fname = join(dist_dir, name)
        elif name == "doc.zip":
            # Documentation file
            fname = join(temp_dir, name)
        else:
            raise ValueError(f"Unknown asset '{name}'")
        r = requests.get(url)
        with open(fname, "wb") as file:
            file.write(r.content)


    # Upload distributions to PyPI
    print("Upload distributions to PyPI...")
    twine_upload([f"{dist_dir}/*"])


    # Upload documentation on host server
    print("Upload documentation to host server...")
    hostname = input("Hostname: ")
    username = input("Username: ")
    password = getpass.getpass()
    html_dir = "./biotite"

    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy)
    client.connect(hostname=hostname, username=username, password=password)
    sftp = client.open_sftp()

    # Place documentation into home directory
    sftp.put(join(temp_dir, "doc.zip"), "./doc.zip")
    # Naviagte into home directory
    remote_exec(client, f"cd /home/{username}")
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
    sftp.close()
