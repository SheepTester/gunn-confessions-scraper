# gunn-confessions-scraper
Scrape stuff from Gunn Confessions' Facebook Page using Python (language diversity!) because Facebook won't give access to their proper APIs

### Python notes

To use Python in Git Bash, you need to add

```sh
alias python='winpty python.exe'
```

to `/etc/bash.bashrc` ([src](https://stackoverflow.com/a/36530750))

Apparently you need to run `python -m venv .venv` to create a virtual environment so PIP can stay separate. (`.venv` is just the directory to put it inside; [`.venv` is a common name apparently](https://docs.python.org/3/library/venv.html#module-venv))

[So then afterwards](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) I must run (in Git Bash; cmd is probably different)

```sh
source .venv/Scripts/activate
```

If it works, you won't forget to do `deactivate` because it'll keep printing `(.venv)` after every command until you run `deactivate`.

Then do whatever `pip install` magic is necessary.

To save requirements.txt, do `pip freeze > requirements.txt`. To load from it, do `pip install -r requirements.txt`

There exists a `pdb` for debugging Python stuff. Do `python -m pdb -c continue scraper.py` to pause on exception ([src](https://stackoverflow.com/a/2438834)). [Commands](https://docs.python.org/3/library/pdb.html#debugger-commands)

`p expression` runs `expression`
