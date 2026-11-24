# 🎯 Offset Watcher 24/7

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-24%2F7-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Discord](https://img.shields.io/badge/Discord-Webhooks-5865F2?style=for-the-badge&logo=discord&logoColor=white)
![Sources](https://img.shields.io/badge/Monitored_Sources-19-2ECC71?style=for-the-badge)

An automated, serverless offset tracker that monitors **19 endpoints across 3 offset providers** for 11 competitive games. Whenever a game updates and new offsets or dumps are published, the bot automatically extracts the `.hpp` or `.json` file and posts it directly to your **Discord** channels.

---

## ⚙️ How It Works

1. **Scheduled Trigger:** Every 15 minutes, an external cron trigger (`cron-job.org`) calls GitHub's `workflow_dispatch` API to start the workflow on time.
2. **Multi-Source Scraping:** `check_offsets.py` queries the APIs of **CheatOffsets**, **KittyHook** (formerly Oshe Offsets), and **Xerozify** across 19 game endpoints.
3. **Version & Build Comparison:** Each fetched build ID, version string, or file hash is compared against the last known version saved in `state.json`.
4. **Instant Discord Delivery:**
   - **Game Channels:** If a new version is detected, the bot posts a rich embed pinging `@Offsets` with the ready-to-use `.hpp` (C++ header) or `.json` dump attached.
   - **Status / Log Channel:** At the end of every scan, a summary embed is sent to your announcements channel showing the UTC timestamp and whether any games were updated.
5. **Automatic State Persistence:** If any updates were found, GitHub Actions automatically commits and pushes the updated `state.json` back to the repository so you never get duplicate alerts.

---

## 🌐 Websites & Data Sources Used

This tracker pulls live offset data from the following three public websites:

1. **[CheatOffsets (`cheatoffsets.com`)](https://www.cheatoffsets.com)**
   - **Endpoint:** `https://www.cheatoffsets.com/api/games/{game}/current`
   - **Output:** Extracts `.json` offset maps or parses C++ `.hpp` code blocks from markdown.
   - **Tracked Games (5):** Fortnite, Rust, FiveM, CS2, Roblox.

2. **[KittyHook (`offsets.kittyhook.vip`)](https://offsets.kittyhook.vip)** — formerly `offsets.oshe.win`, same API.
   - **Endpoints:** `https://offsets.kittyhook.vip/api/{game}/latest` & `https://offsets.kittyhook.vip/games/{game}/{file}`
   - **Output:** Downloads `offsets.hpp` / `Offsets.hpp` / `client_dll.hpp` directly (falls back to `offsets.json` if unavailable).
   - **Tracked Games (10):** Fortnite, Rust, FiveM, CS2, Roblox, Rob Run, Retrac, Valorant, Wardogs, Apex Legends.
   - **Also available upstream (not tracked):** Blood Strike, Overwatch 2.

3. **[Xerozify (`xerozify.xyz`)](https://xerozify.xyz)**
   - **Endpoint:** `https://xerozify.xyz/api/offsets/games/{game}/current`
   - **Output:** Extracts structured `.json` dumps or C++ `.hpp` headers.
   - **Tracked Games (4):** Rust, Rainbow Six Siege, FiveM, Valorant.

### Coverage Matrix & Required Secrets

| Game | CheatOffsets | KittyHook | Xerozify | Default Webhook Secret |
| :--- | :---: | :---: | :---: | :--- |
| **Fortnite** | ✅ | ✅ | — | `WEBHOOK_OFFSETS` |
| **Rust** | ✅ | ✅ | ✅ | `WEBHOOK_OFFSETS` |
| **FiveM** | ✅ | ✅ | ✅ | `WEBHOOK_OFFSETS` |
| **CS2** | ✅ | ✅ | — | `WEBHOOK_OFFSETS` |
| **Roblox** | ✅ | ✅ | — | `WEBHOOK_OFFSETS` |
| **Valorant** | — | ✅ | ✅ | `WEBHOOK_OFFSETS` |
| **Rainbow Six Siege** | — | — | ✅ | `WEBHOOK_OFFSETS` |
| **Rob Run** | — | ✅ | — | `WEBHOOK_OFFSETS` |
| **Retrac** | — | ✅ | — | `WEBHOOK_OFFSETS` |
| **Wardogs** | — | ✅ | — | `WEBHOOK_OFFSETS` |
| **Apex Legends** | — | ✅ | — | `WEBHOOK_OFFSETS` |
| **Scan Log / Status** | *All* | *All* | *All* | `WEBHOOK_LOG` |

> Every game falls back to `WEBHOOK_OFFSETS`, so **two secrets are enough** to get started. If you ever want a specific game in its own channel, add that game's override secret (`WEBHOOK_FORTNITE`, `WEBHOOK_RUST`, `WEBHOOK_FIVEM`, `WEBHOOK_CS2`, `WEBHOOK_ROBLOX`, `WEBHOOK_ROBRUN`, `WEBHOOK_RETRAC`, `WEBHOOK_VALORANT`, `WEBHOOK_R6`, `WEBHOOK_WARDOGS`, `WEBHOOK_APEX`) and it wins over the default.

---

## 📖 Setup & Installation Manual

Follow these steps to deploy your own 24/7 instance completely free—no VPS or local PC required.

### Step 1: Fork the Repository
1. Click the **Fork** button at the top-right corner of this repository to copy it to your GitHub account.
2. Keep your forked repository **Public**. GitHub provides **unlimited free Actions minutes** for public repositories, allowing the bot to run every 15 minutes all year at zero cost.

### Step 2: Create Discord Webhooks
1. Open your Discord server and go to **Edit Channel** (gear icon) → **Integrations** → **Webhooks** → **New Webhook** for each game channel you want to receive alerts in.
2. Create one additional webhook in a dedicated status/log channel (e.g., `#announcements` or `#scan-logs`).
3. Copy each webhook URL.

### Step 3: Add Webhooks to GitHub Secrets
Never paste webhook URLs directly into the code. Store them securely as encrypted secrets:
1. In your forked GitHub repository, go to **Settings** → **Secrets and variables** → **Actions**.
2. Click **New repository secret**.
3. Create these two secrets and paste the matching Discord webhook URL as each value:

   | Secret name | Value |
   | :--- | :--- |
   | `WEBHOOK_OFFSETS` | the webhook of the channel that should receive every game's offsets |
   | `WEBHOOK_LOG` | the webhook of the scan log / status channel |

   > **Tip:** Both are optional — the script prints `[config] ... MISSING` in the Actions log and simply skips anything without a webhook. To split games across channels later, add the per-game overrides from the table above.

### Step 4: Enable Workflow Write Permissions
The bot needs permission to update `state.json` inside your repository whenever a new build is detected:
1. Go to **Settings** → **Actions** → **General**.
2. Scroll down to **Workflow permissions**.
3. Select **Read and write permissions** and click **Save**.

### Step 5: Automation (Built In)
The workflow already schedules itself every 15 minutes (`schedule` → `cron: '*/15 * * * *'` in `.github/workflows/watcher.yaml`), so nothing else is needed to keep it running 24/7.

GitHub can delay scheduled runs during peak hours. If you want exact timing, you can also trigger it externally through the `workflow_dispatch` API with a free `cron-job.org` account:
1. **Create a GitHub Token:**
   - Go to your GitHub profile **Settings** (top-right avatar) → **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token (classic)**.
   - Give it a name (e.g., `offset-watcher`), set expiration to **No expiration**, check the **`workflow`** scope, and copy the generated token.
2. **Configure the Cron Job:**
   - Sign up for a free account at [cron-job.org](https://cron-job.org) and click **Create cronjob**.
   - **Title:** `Offset Watcher`
   - **URL:** `https://api.github.com/repos/YOUR_GITHUB_USERNAME/offset-watcher/actions/workflows/watcher.yaml/dispatches` *(replace `YOUR_GITHUB_USERNAME` with your username)*
   - **Execution schedule:** Every **15 minutes**
   - Switch to the **Advanced** tab and set:
     - **Request method:** `POST`
     - **Headers:**
       - `Authorization`: `Bearer YOUR_GITHUB_TOKEN`
       - `Accept`: `application/vnd.github+json`
       - `User-Agent`: `offset-watcher`
     - **Request body:**
       ```json
       {"ref":"main"}
       ```
   - Click **Create**.

### Step 6: Run Your First Test
1. Go to the **Actions** tab in your GitHub repository.
2. Select **Check Offsets** on the left sidebar, click **Run workflow** → **Run workflow**.
3. Within ~20 seconds, your Discord status channel should receive the **Offset Scan Log** embed, and any newly detected builds will be posted to their respective game channels.

---

## 📁 Repository Structure

```text
offset-watcher/
├── .github/
│   └── workflows/
│       └── watcher.yaml   # GitHub Actions workflow definition & auto-commit step
├── check_offsets.py       # Scraper, parser, and Discord webhook notifier
├── state.json             # Stores the latest notified build/version ID per source
└── README.md              # Documentation & setup guide
```
## 📄 Support
* **Support:** If you find **Offsets Watcher** useful, consider supporting future updates on [Ko-fi](https://ko-fi.com/drjhn291).
