# Git Archiver

Archive and save your git repository including all branches locally.

## Installation

```bash
git clone https://github.com/marcusfrdk/git-archiver
```

## Requirements

- Python 3.8 or above

## How to use

```bash
python main.py URL
```

Run the script with one or many urls to your git repository and the script will checkout all branches and make sure you have saved all your code locally if you want to delete your remote repository.

You can also provide the urls in the `urls.py` list and run the script with no arguments.

## Flags

### Force (-f, --force)

The force flag skips any confirmation in the script.
