# gunn-confessions-scraper
Scrape stuff from Gunn Confessions' Facebook Page using Python (language diversity!) because Facebook won't give access to their proper APIs

Try running

```sh
python get_all.py
```

### Attempts

1. **Attempt 1**: The Facebook API would be ideal; however, in order to fetch public pages from other people, you need to request permission from Facebook. To do so, you first must make a working demonstration of what you're making (they assume everyone uses the API for Facebook integration in mobile apps, for some reason), which is rather difficult given that you can't make a demo of something using something that you're asking for because you don't have it. Anyways, I ended up making my own test confessions page, but since it worked, I guess Facebook thought the special permission wasn't needed, so they rejected my request.

2. **Attempt 2**: Scraping the web pages could be done in any language, but I chose Python because language diversity is important, and I heard Python was good for it. This works, but searching got me rate-limited by IP. I'm not sure if this is a permanent ban.

3. **Attempt 3**: A userscript that automatically searches Facebook is probably the most hacky solution. For some reason, the rate-limit was only enforced when signed out, so I made a userscript to automatically search while signed in. Eventually, I got rate-limited again, but at least it gave a friendly notice that it was only temporary.

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

- `p expression` runs `expression`

I should learn about PYTHONICISM
