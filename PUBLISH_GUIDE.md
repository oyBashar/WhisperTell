# How to Publish WhisperTell on GitHub

A complete step-by-step guide for publishing WhisperTell under your GitHub account **oyBashar**.

---

## Part 1 — Set Up Git on Termux (First Time Only)

### Step 1 — Install Git
```bash
pkg install git -y
```

### Step 2 — Set your identity
```bash
git config --global user.name "oyBashar"
git config --global user.email "your@email.com"
```
*(Replace with your real email — it doesn't have to be public)*

### Step 3 — Generate an SSH key (safest login method)
```bash
ssh-keygen -t ed25519 -C "your@email.com"
```
Press Enter 3 times to accept defaults (no passphrase is fine for personal use).

### Step 4 — Copy your public key
```bash
cat ~/.ssh/id_ed25519.pub
```
Copy the entire line that appears. It starts with `ssh-ed25519`.

### Step 5 — Add key to GitHub
1. Open **github.com** in your browser
2. Go to **Settings → SSH and GPG keys → New SSH key**
3. Title: `Termux` (or any name)
4. Paste the key → click **Add SSH key**

### Step 6 — Test the connection
```bash
ssh -T git@github.com
```
You should see: `Hi oyBashar! You've successfully authenticated.`

---

## Part 2 — Create the GitHub Repository

### Step 1 — Go to GitHub
Open **github.com/new** in your browser.

### Step 2 — Fill in the details
- **Repository name:** `WhisperTell`
- **Description:** `Serverless terminal chat for Termux & Linux — LAN + Worldwide via MQTT`
- **Visibility:** ✅ Public *(so others can find and clone it)*
- **Initialize:** ❌ Do NOT check "Add README" (you already have one)
- Click **Create repository**

---

## Part 3 — Push WhisperTell to GitHub (from Termux)

### Step 1 — Go into your WhisperTell folder
```bash
cd WhisperTell
```

### Step 2 — Initialize Git
```bash
git init
```

### Step 3 — Add all files
```bash
git add .
```

### Step 4 — Make the first commit
```bash
git commit -m "Initial release — WhisperTell v2.0"
```

### Step 5 — Connect to your GitHub repo
```bash
git remote add origin git@github.com:oyBashar/WhisperTell.git
```

### Step 6 — Push everything
```bash
git branch -M main
git push -u origin main
```

### Step 7 — Done!
Visit **github.com/oyBashar/WhisperTell** — your project is now live.

---

## Part 4 — Make It Look Good on GitHub

### Add Topics (Tags) so people can find it
1. Go to your repo page
2. Click the ⚙️ gear icon next to **About**
3. Add topics: `termux`, `python`, `chat`, `terminal`, `mqtt`, `lan`, `android`, `cli`
4. Add the description: `Serverless terminal chat for Termux & Linux — LAN + Worldwide via MQTT`
5. Save

### Create a Release (Optional but recommended)
1. On your repo page, click **Releases → Create a new release**
2. Tag: `v2.0`
3. Title: `WhisperTell v2.0 — LAN + Worldwide Chat`
4. Describe the release
5. Attach the `.zip` file if you want
6. Click **Publish release**

---

## Part 5 — Share WhisperTell With Others

Once published, anyone can install it with:

```bash
git clone https://github.com/oyBashar/WhisperTell.git
cd WhisperTell
pip install paho-mqtt
python3 whispertell.py
```

### Share on communities:
- **Reddit:** r/termux, r/commandline, r/Python, r/selfhosted
- **GitHub Topics:** Your tags make it discoverable
- **Telegram:** Termux groups

---

## Part 6 — Updating WhisperTell Later

Whenever you make changes:

```bash
# Edit files...
git add .
git commit -m "What you changed"
git push
```

Users update with:
```bash
cd WhisperTell
git pull
```

---

## Quick Reference

| Task | Command |
|------|---------|
| First push | `git init && git add . && git commit -m "msg" && git push -u origin main` |
| Update | `git add . && git commit -m "msg" && git push` |
| Check status | `git status` |
| See history | `git log --oneline` |

---

*Made by oyBashar — github.com/oyBashar*
