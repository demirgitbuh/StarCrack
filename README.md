<div align="center">

<img src="https://readme-typing-svg.demolab.com/?lines=StarCrack+%E2%97%86+Hash+Cracking+TUI;Dictionary+%2B+Brute-force+attacks;MD5+%E2%80%A2+SHA1+%E2%80%A2+SHA256+%E2%80%A2+SHA512;Built+with+Rich+%2B+Python&font=Fira%20Code&size=22&pause=1200&color=3BA7FF&center=true&vCenter=true&width=720&height=55" alt="StarCrack" />

<br />

![version](https://img.shields.io/badge/version-0.1.0-3BA7FF?style=for-the-badge&labelColor=0D1117)
![python](https://img.shields.io/badge/python-3.10%2B-3BA7FF?style=for-the-badge&logo=python&logoColor=white&labelColor=0D1117)
![rich](https://img.shields.io/badge/TUI-rich-3BA7FF?style=for-the-badge&labelColor=0D1117)
![license](https://img.shields.io/badge/license-MIT-3BA7FF?style=for-the-badge&labelColor=0D1117)
![platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20mac-3BA7FF?style=for-the-badge&labelColor=0D1117)

<br />

<img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/palette/macchiato.png" width="0" height="0" alt="" />

<h3>◆ A modern terminal hash cracker with a slick Rich-powered UI ◆</h3>

<sub>Dictionary & brute-force · auto hash detection · live progress · JSON reports</sub>

</div>

<br />

---

## ✦ Features

- **Interactive TUI** — launch with no args, drive everything from a blue/grey themed menu
- **Dictionary attack** — rip through wordlists line-by-line with a live progress bar
- **Brute-force attack** — `itertools.product` across lowercase / uppercase / digits / symbols / all
- **Auto hash detection** — MD5 · SHA1 · SHA256 · SHA512 recognized by length
- **Live progress** — spinner, percentage bar, hashes/sec, attempts counter, elapsed time
- **Result panels** — `✓ CRACKED` in green, `✗ NOT FOUND` in red — both saved to `./data/results.txt`
- **JSON reports** — optional `-o report.json` for machine-readable output
- **Graceful Ctrl+C** — partial stats are still persisted before exit
- **Zero heavy deps** — only `rich`, everything else is stdlib

<br />

## ✦ Install

```bash
git clone https://github.com/<you>/StarCrack.git
cd StarCrack
pip install -r requirements.txt
```

<sub>Requires Python 3.10+. Only dependency: <code>rich</code>.</sub>

<br />

## ✦ Usage

### Interactive TUI

```bash
python starcrack.py
```

```text
┌─────────────────────────────────────────┐
│           ◆ StarCrack  v0.1.0           │
│           Hash Cracking Tool            │
│  ─────────────────────────────────────  │
│          2026-04-19  01:33:37           │
└─────────────────────────────────────────┘
┌─ ◆ Main Menu ───────────────────────────┐
│  1  ›  Dictionary Attack      wordlist  │
│  2  ›  Brute-force Attack    itertools  │
│  3  ›  View Last Results        ./data  │
│  q  ›  Quit                       exit  │
└──────────── select an action ───────────┘
```

### CLI mode

```bash
# Dictionary attack
python starcrack.py -h 5f4dcc3b5aa765d61d8327deb882cf99 -m dict -w rockyou.txt

# Brute-force attack (lowercase, max length 5)
python starcrack.py -h <hash> -m brute -c lowercase -l 5

# With JSON report
python starcrack.py -h <hash> -m dict -w rockyou.txt -o report.json
```

<br />

## ✦ Flags

| Flag | Description | Example |
|------|-------------|---------|
| `-h` / `-H` | Target hash | `-h 5f4dcc3b...` |
| `-m` | Mode: `dict` \| `brute` | `-m brute` |
| `-w` | Wordlist (dict mode) | `-w rockyou.txt` |
| `-c` | Charset (brute mode) | `-c all` |
| `-l` | Max length (brute mode) | `-l 6` |
| `-a` | Override algorithm | `-a sha256` |
| `-o` | JSON report path | `-o report.json` |

**Charsets:** `lowercase` · `uppercase` · `digits` · `symbols` · `all`

<br />

## ✦ Hash Detection

| Length | Algorithm |
|:------:|:---------:|
| 32 | MD5 |
| 40 | SHA1 |
| 64 | SHA256 |
| 128 | SHA512 |

<br />

## ✦ Output

All runs append to `./data/results.txt`:

```text
[2026-04-19T01:20:14] 5f4dcc3b5aa765d61d8327deb882cf99 | md5 | dict | cracked | password
```

With `-o report.json`:

```json
{
  "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
  "hash_type": "md5",
  "mode": "dict",
  "result": "cracked",
  "plaintext": "password",
  "attempts": 3,
  "duration": 0.0173,
  "timestamp": "2026-04-19T01:20:14"
}
```

<br />

## ✦ Project Layout

```
StarCrack/
├─ starcrack.py        # single-file TUI + CLI
├─ requirements.txt    # rich
├─ data/               # results.txt lives here
├─ LICENSE
└─ README.md
```

<br />

## ✦ Disclaimer

> StarCrack is for **educational, CTF, and authorized security testing** only.
> Do not use it against systems, accounts, or data you don't own or have explicit permission to test.

<br />

## ✦ License

Released under the [MIT License](LICENSE).

<br />

<div align="center">

<sub>◆ built with python · rich · hashlib ◆</sub>

</div>
