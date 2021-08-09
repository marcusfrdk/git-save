# Git Archiver

Download your old git repository that you no longer want to keep on your Github, Gitlab or other git hosts.

_All this script does is clone the specified repository and checks out all branches to keep a copy of the branch locally_

## Installation

```bash
$ git clone https://github.com/marcusfrdk/git-archiver
```

## Requirements

- Python 3

## How to use

```bash
$ python archive.py url
```

All this script takes in is a url to your git repository. It will check for all branches and make sure you have downloaded them so you can use **every branch** without the existence of the remote repository.

## Optional flags

### Compress (-c, --compress)

Create a zip archive from the generated folder.

### Verbose (-v, --verbose)

Log activity from script
