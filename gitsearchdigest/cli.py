import hashlib
import pathlib
import argparse
import subprocess
import sys
import os

def git_digest(filename):
    filesize = os.path.getsize(filename)
    m = hashlib.sha1()
    m.update(b"blob %u\0" % filesize)
    with open(filename, "rb") as f:
        m = hashlib.file_digest(f, lambda: m)
    return m.hexdigest()

def main():
    parser = argparse.ArgumentParser(
        description="search git repositories for digests of files",
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )
    parser.add_argument(
        "-C",
        metavar='<path>',
        type=pathlib.Path,
        help="path to git repository",
        required=True
    )
    args = parser.parse_args()
    for filename in filter(None, sys.stdin.buffer.read().split(b'\x00')):
        filename = filename.decode('utf-8')
        try:
            digest = git_digest(filename)
        except:
            continue
        commits = subprocess.run(["git", "-C", args.C, "rev-list", "--all", "--", filename], stdout=subprocess.PIPE)
        for commit in filter(None, commits.stdout.decode('utf-8').split("\n")):
            d = subprocess.run(["git", "-C", args.C, "rev-parse", f"{commit}:{filename}"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            d = d.stdout.decode('utf-8').rstrip()            
            if d == digest:
                print(f"{commit}  {filename}")
                break
