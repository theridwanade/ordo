# **ORDO**

> I don’t know why I named it *Ordo*. I just did. Turns out it means *order* in Latin — which checks out, because this thing forces order on chaos.
> (Also yes — right now Ordo is basically built for **MovieBox**. If you use something else, it *might* work… or it might sulk and do nothing. Welcome to alpha software.)

---

Ordo is a tiny, opinionated Python CLI I made because **Android 13+ and MovieBox make moving files a pain in the soul**.
It finds movie files inside the MovieBox app folder, copies them to a structured archive on your drive, and tags them so you can stop living in a folder soup.

Although it started as a MovieBox helper, I don’t plan to stop there.
My goal is to evolve Ordo into a **general-purpose file automation tool** — something that can handle any copy or move task I throw at it. For now though, it’s *movies first*.

> So yeah — this README is going to change as the tool grows (or maybe never, because explaining my code is harder than writing it).

---

## ⚠️ **Important — MovieBox first, others maybe later**

Right now, Ordo is **basically exclusive to MovieBox**, because that’s what I built it for.
It looks for the movie and subtitle files that MovieBox leaves behind in its app directory structure.
If you try random folders, you might get lucky — or nothing at all. That’s fine. Life’s like that.

> The way Ordo organizes files follows my personal philosophy: I sort movies by their **country or origin** (like *Chinese*, *American*, *Korean*, *Japanese*, etc.),
> and I pack all subtitles together in a single subfolder.
> Maybe I’ll handle subtitle languages properly later — for now, I just dump them all in and it works.

If you want Ordo to support other apps, feel free to fork it or open an issue.

> And if you *do* fork it, tell me. I’d love to see what you build on top of it.

---

## 🚀 **Quickstart — Install & Run**

You only need Python and a little patience.

```bash
# Clone the repo
git clone https://github.com/theridwanade/ordo.git
# or, if you’re fancy:
git clone git@github.com:theridwanade/ordo.git

cd ordo

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 ordo.py
# or if you're on Windows (why though?)
python ordo.py
```

Later, I might turn it into a proper CLI command (`pip install -e .` → `ordo`).
For now, `python ordo.py` is the move.

---

## 🧭 **Basic Workflow (What You’ll Actually Do)**

1. **Add a source** — tell Ordo where MovieBox stores files on your device (or where you extracted your backup).
   This includes both *movie* and *subtitle* sources since MovieBox keeps them separately.
2. **Add a destination** — tell Ordo where to put the organized files (usually a folder on your laptop or external drive).
3. **Load / scan** — Ordo scans your source folders to find movies and subtitles.
4. **Tag** — assign tags or categories to movies (e.g. `Anime`, `American Movie`).
   There’s a default tag hardcoded in the script — change it if you like.
   *Future goal:* AI-assisted tagging.
5. **Copy / organize** — Ordo copies the files to your destination in a tidy structure:

   ```
   DESTINATION/<tag>/<movie_name>/
   ```
6. **Save configuration** — Ordo remembers your sources and destination for next time in `sources.json`.

---

## 💬 **Things You Should Know**

* Ordo **copies**, it doesn’t move or delete. Your source files stay untouched.
* It’s **alpha software** — still rough around the edges. If it breaks, fix it or open an issue.
* It *might not work for you at all*, but it works perfectly for me — and that’s what matters.
* I wrote this in a few hours; it’s functional, not polished.
  If you want polish, buy a commercial product. Or better yet, write your own — this is piracy land.

---

## ✨ **Roadmap (If I Feel Generous)**

* 🤖 AI-assisted tagging — guess tags from filenames or cover art.
* 🎞️ Better multi-app support (not just MovieBox).
* 🖥️ A tiny web UI for lazy moments (don’t count on it anytime soon).

---

## 🧾 **Tech Stack**

* **Python 3.12**
* [`tqdm`](https://github.com/tqdm/tqdm) — progress bars
* [`questionary`](https://github.com/tmbo/questionary) — interactive prompts
* `shutil`, `pathlib`, `os` — boring but essential file work

---

## 🎩 **Final Words (Short & Smug)**

Ordo is a revenge tool against **disorganized downloads** and **restrictive Android permissions**.
It’s not corporate, not shiny, and definitely not perfect — but it’s mine.
And it works.

I built it to save time… then spent hours writing it anyway.

[![wakatime](https://wakatime.com/badge/user/efadc313-4de0-4714-bc63-9a49ac07dd6e/project/a41030a8-9e3a-4789-a82b-8a3ea95cb637.svg)](https://wakatime.com/badge/user/efadc313-4de0-4714-bc63-9a49ac07dd6e/project/a41030a8-9e3a-4789-a82b-8a3ea95cb637)

Use it. Break it. Send issues. Or don’t.
At least now you’ll have a little **order where there used to be chaos.**

