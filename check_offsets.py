from datetime import datetime, timezone
import hashlib
import json
import os
import re
import requests

# --- WEBHOOKS LOADED FROM GITHUB SECRETS ---
# Two-secret setup:
#   WEBHOOK_OFFSETS -> all game alerts (default for every game channel)
#   WEBHOOK_LOG     -> the scan log / status channel
# Optional per-game overrides (take priority over WEBHOOK_OFFSETS):
#   WEBHOOK_FORTNITE, WEBHOOK_RUST, WEBHOOK_FIVEM, WEBHOOK_CS2, WEBHOOK_ROBLOX,
#   WEBHOOK_ROBRUN, WEBHOOK_RETRAC, WEBHOOK_VALORANT, WEBHOOK_R6
# WEBHOOK_ANUNCIOS is still accepted as an alias for WEBHOOK_LOG.
OFFSETS_WEBHOOK = os.environ.get("WEBHOOK_OFFSETS", "").strip()
LOG_WEBHOOK = (os.environ.get("WEBHOOK_LOG") or os.environ.get("WEBHOOK_ANUNCIOS") or "").strip()


def game_webhook(name):
    return os.environ.get(f"WEBHOOK_{name.upper()}", "").strip() or OFFSETS_WEBHOOK


WEBHOOKS = {
    "announcements": LOG_WEBHOOK,
    "fortnite": game_webhook("fortnite"),
    "rust": game_webhook("rust"),
    "fivem": game_webhook("fivem"),
    "cs2": game_webhook("cs2"),
    "roblox": game_webhook("roblox"),
    "robrun": game_webhook("robrun"),
    "retrac": game_webhook("retrac"),
    "valorant": game_webhook("valorant"),
    "r6": game_webhook("r6"),
    "wardogs": game_webhook("wardogs"),
    "apex": game_webhook("apex"),
}

ANNOUNCEMENTS_WEBHOOK = WEBHOOKS["announcements"]

print(f"[config] offsets webhook: {'set' if OFFSETS_WEBHOOK else 'MISSING'} | "
      f"log webhook: {'set' if ANNOUNCEMENTS_WEBHOOK else 'MISSING'}")

GAMES = [
    {
        "slug": "fortnite",
        "label": "Fortnite",
        "color": 0x00D4FF,
        "webhook": WEBHOOKS["fortnite"]
    },
    {
        "slug": "rust",
        "label": "Rust",
        "color": 0xCE422B,
        "webhook": WEBHOOKS["rust"]
    },
    {
        "slug": "fivem",
        "label": "FiveM",
        "color": 0xF5A623,
        "webhook": WEBHOOKS["fivem"]
    },
    {
        "slug": "cs2",
        "label": "CS2",
        "color": 0xF0A500,
        "webhook": WEBHOOKS["cs2"]
    },
    {
        "slug": "roblox",
        "label": "Roblox",
        "color": 0xFF0000,
        "webhook": WEBHOOKS["roblox"]
    }
]

# offsets.oshe.win moved to offsets.kittyhook.vip (identical API).
# State keys keep the historical "oshe_" prefix so the host switch does not
# re-post every game that was already notified.
KITTYHOOK_STATE_PREFIX = "oshe_"

KITTYHOOK_GAMES = [
    # --- 5 shared games ---
    {
        "slug": "fortnite",
        "alt_slugs": [],
        "label": "Fortnite",
        "engine": "Unreal Engine 5",
        "hpp_files": ["offsets.hpp", "Offsets.hpp"],
        "color": 0x00D4FF,
        "webhook": WEBHOOKS["fortnite"]
    },
    {
        "slug": "rust",
        "alt_slugs": [],
        "label": "Rust",
        "engine": "Unity IL2CPP",
        "hpp_files": ["offsets.hpp", "Offsets.hpp"],
        "color": 0xCE422B,
        "webhook": WEBHOOKS["rust"]
    },
    {
        "slug": "fivem",
        "alt_slugs": [],
        "label": "FiveM",
        "engine": "GTA V (RAGE)",
        "hpp_files": ["offsets.hpp", "Offsets.hpp"],
        "color": 0xF5A623,
        "webhook": WEBHOOKS["fivem"]
    },
    {
        "slug": "cs2",
        "alt_slugs": [],
        "label": "CS2",
        "engine": "Source 2",
        "hpp_files": ["client_dll.hpp", "offsets.hpp", "Offsets.hpp"],
        "color": 0xF0A500,
        "webhook": WEBHOOKS["cs2"]
    },
    {
        "slug": "roblox",
        "alt_slugs": [],
        "label": "Roblox",
        "engine": "Roblox Engine / Luau",
        "hpp_files": ["offsets.hpp", "Offsets.hpp"],
        "color": 0xFF0000,
        "webhook": WEBHOOKS["roblox"]
    },
    # --- 3 Oshe-exclusive games ---
    {
        "slug": "robrun",
        "alt_slugs": ["rob-run"],
        "label": "Rob Run",
        "engine": "Kefir IL2CPP",
        "hpp_files": ["offsets.hpp", "Offsets.hpp"],
        "color": 0x9B59B6,
        "webhook": WEBHOOKS["robrun"]
    },
    {
        "slug": "retrac",
        "alt_slugs": [],
        "label": "Retrac",
        "engine": "Unreal Engine",
        "hpp_files": ["Offsets.hpp", "offsets.hpp"],
        "color": 0x2ECC71,
        "webhook": WEBHOOKS["retrac"]
    },
    {
        "slug": "valorant",
        "alt_slugs": [],
        "label": "Valorant",
        "engine": "Unreal Engine 4.27 (VGK)",
        "hpp_files": ["Offsets.hpp", "offsets.hpp"],
        "color": 0xFF4655,
        "webhook": WEBHOOKS["valorant"]
    },
    # --- KittyHook-only games ---
    {
        "slug": "wardogs",
        "alt_slugs": [],
        "label": "Wardogs",
        "engine": "Unreal Engine 5.7",
        "hpp_files": ["offsets.hpp", "Offsets.hpp"],
        "color": 0x1ABC9C,
        "webhook": WEBHOOKS["wardogs"]
    },
    {
        "slug": "apex",
        "alt_slugs": ["apexlegends", "apex-legends"],
        "label": "Apex Legends",
        "engine": "Source Engine",
        "hpp_files": ["offsets.hpp", "Offsets.hpp"],
        "color": 0xDA292A,
        "webhook": WEBHOOKS["apex"]
    }
]

XEROZIFY_GAMES = [
    {
        "slug": "rust",
        "label": "Rust",
        "color": 0xCE422B,
        "webhook": WEBHOOKS["rust"]
    },
    {
        "slug": "r6",
        "label": "Rainbow Six Siege",
        "color": 0x3498DB,
        "webhook": WEBHOOKS["r6"]
    },
    {
        "slug": "fivem",
        "label": "FiveM",
        "color": 0xF5A623,
        "webhook": WEBHOOKS["fivem"]
    },
    {
        "slug": "valorant",
        "label": "Valorant",
        "color": 0xFF4655,
        "webhook": WEBHOOKS["valorant"]
    }
]

STATE_FILE = "state.json"
CHEATOFFSETS_URL = "https://www.cheatoffsets.com/api"
KITTYHOOK_URL = "https://offsets.kittyhook.vip"
XEROZIFY_URL = "https://xerozify.xyz/api/offsets/games"


def has_valid_offsets(offsets_dict):
    if not offsets_dict or not isinstance(offsets_dict, dict):
        return False
    for val in offsets_dict.values():
        if isinstance(val, str) and (val.startswith("0x") or val.startswith("0X")):
            return True
        if isinstance(val, int) and val > 0:
            return True
        if isinstance(val, dict) and has_valid_offsets(val):
            return True
    return False


def extract_cpp_from_markdown(md_text):
    if not md_text:
        return ""
    blocks = re.findall(r"```(?:cpp|c\+\+|c|hpp|h)?\s*\n(.*?)```", md_text, re.DOTALL | re.IGNORECASE)
    if blocks:
        return "\n\n// ==========================================\n\n".join(b.strip() for b in blocks)
    return md_text.strip()


def extract_xerozify_payload(data):
    for key in ["offsets_flat", "offsets", "data", "dump"]:
        candidate = data.get(key)
        if isinstance(candidate, dict) and has_valid_offsets(candidate):
            return json.dumps(candidate, indent=2), "json", "application/json"

    for key in ["hpp", "header", "raw", "content", "code", "markdown", "text"]:
        candidate = data.get(key)
        if isinstance(candidate, str) and candidate.strip():
            extracted = extract_cpp_from_markdown(candidate)
            if extracted:
                return extracted, "hpp", "text/plain"

    for key, val in data.items():
        if isinstance(val, dict) and has_valid_offsets(val):
            return json.dumps(val, indent=2), "json", "application/json"
        if isinstance(val, str) and ("0x" in val or "constexpr" in val or "#define" in val):
            return extract_cpp_from_markdown(val), "hpp", "text/plain"

    return json.dumps(data, indent=2), "json", "application/json"


if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
else:
    state = {}

updated = False
updated_summary = []
search_time = datetime.now(timezone.utc).strftime("%H:%M:%S UTC (%Y-%m-%d)")

# 1. Check games on cheatoffsets.com
for game in GAMES:
    slug = game["slug"]
    try:
        res = requests.get(f"{CHEATOFFSETS_URL}/games/{slug}/current", timeout=15)
        if res.status_code != 200:
            print(f"[{slug}] HTTP Error {res.status_code}")
            continue

        data = res.json()
        current_id = str(data.get("id"))
        version = data.get("version", "Unknown")
        label = data.get("label", "")

        if state.get(slug) != current_id:
            print(f"[{slug}] New update detected: Build {current_id}")
            embed = {
                "title": f"{game['label']} offsets updated",
                "description": f"**Version:** `{version}`\n**Note:** {label if label else 'No notes'}",
                "url": f"https://www.cheatoffsets.com/games/{slug}",
                "color": game["color"],
                "footer": {"text": "cheatoffsets.com"},
                "timestamp": data.get("updated_at")
            }
            payload = {"content": "@Offsets", "embeds": [embed]}

            offsets_data = data.get("offsets", {})
            if has_valid_offsets(offsets_data):
                content_str = json.dumps(offsets_data, indent=2)
                filename = f"{slug}_offsets_{version}.json"
                mime_type = "application/json"
            else:
                cpp_code = extract_cpp_from_markdown(data.get("markdown", ""))
                content_str = cpp_code if cpp_code else json.dumps(data, indent=2)
                filename = f"{slug}_offsets_{version}.hpp"
                mime_type = "text/plain"

            files = {"file": (filename, content_str, mime_type)}
            if game["webhook"]:
                requests.post(game["webhook"], data={"payload_json": json.dumps(payload)}, files=files, timeout=15)
            state[slug] = current_id
            updated = True
            updated_summary.append(f"**{game['label']}** (`cheatoffsets.com` · `{version}`)")
        else:
            print(f"[{slug}] No changes.")
    except Exception as e:
        print(f"[{slug}] Error: {e}")

# 2. Check all games on offsets.kittyhook.vip (formerly offsets.oshe.win)
for game in KITTYHOOK_GAMES:
    slug = game["slug"]
    state_key = f"{KITTYHOOK_STATE_PREFIX}{slug}"
    try:
        meta_res = None
        actual_slug = slug
        for candidate in [slug] + game.get("alt_slugs", []):
            r = requests.get(f"{KITTYHOOK_URL}/api/{candidate}/latest", timeout=20)
            if r.status_code == 200:
                meta_res = r
                actual_slug = candidate
                break

        if not meta_res:
            print(f"[kittyhook:{slug}] Could not fetch /latest")
            continue

        meta = meta_res.json()
        build_id = str(meta.get("build") or meta.get("sha256") or meta.get("version"))

        if state.get(state_key) != build_id:
            print(f"[kittyhook:{slug}] New update detected: Build {build_id}")

            content_str = None
            filename = None
            mime_type = "text/plain"
            used_url = f"{KITTYHOOK_URL}/games/{actual_slug}/offsets.json"

            for hpp_name in game.get("hpp_files", ["offsets.hpp"]):
                hpp_res = requests.get(f"{KITTYHOOK_URL}/games/{actual_slug}/{hpp_name}", timeout=20)
                if hpp_res.status_code == 200 and hpp_res.text.strip():
                    content_str = hpp_res.text
                    filename = f"{slug}_kittyhook_{build_id}.hpp"
                    used_url = f"{KITTYHOOK_URL}/games/{actual_slug}/{hpp_name}"
                    break

            if not content_str:
                json_res = requests.get(f"{KITTYHOOK_URL}/games/{actual_slug}/offsets.json", timeout=20)
                if json_res.status_code == 200 and json_res.text.strip():
                    content_str = json_res.text
                    filename = f"{slug}_kittyhook_{build_id}.json"
                    mime_type = "application/json"

            if not content_str:
                print(f"[kittyhook:{slug}] No downloadable file yet, will retry next scan.")
                continue

            embed = {
                "title": f"{game['label']} offsets updated",
                "description": f"**Build:** `{build_id}`\n**Engine:** {game['engine']}",
                "url": used_url,
                "color": game["color"],
                "footer": {"text": "offsets.kittyhook.vip"}
            }
            payload = {"content": "@Offsets", "embeds": [embed]}
            files = {"file": (filename, content_str, mime_type)}

            if game["webhook"]:
                requests.post(game["webhook"], data={"payload_json": json.dumps(payload)}, files=files, timeout=20)
            state[state_key] = build_id
            updated = True
            updated_summary.append(f"**{game['label']}** (`offsets.kittyhook.vip` · `{build_id}`)")
        else:
            print(f"[kittyhook:{slug}] No changes.")
    except Exception as e:
        print(f"[kittyhook:{slug}] Error: {e}")

# 3. Check games on xerozify.xyz
for game in XEROZIFY_GAMES:
    slug = game["slug"]
    state_key = f"xerozify_v2_{slug}"
    try:
        res = requests.get(f"{XEROZIFY_URL}/{slug}/current", timeout=15)
        if res.status_code != 200:
            print(f"[xerozify:{slug}] HTTP Error {res.status_code}")
            continue

        data = res.json()
        content_str, ext, mime_type = extract_xerozify_payload(data)

        version = str(
            data.get("version")
            or data.get("build")
            or data.get("id")
            or hashlib.sha256(content_str.encode("utf-8")).hexdigest()[:12]
        )

        if state.get(state_key) != version:
            print(f"[xerozify:{slug}] New update detected: {version}")
            embed = {
                "title": f"{game['label']} offsets updated",
                "description": f"**Version / ID:** `{version}`",
                "url": f"{XEROZIFY_URL}/{slug}/current",
                "color": game["color"],
                "footer": {"text": "xerozify.xyz"}
            }
            payload = {"content": "@Offsets", "embeds": [embed]}
            filename = f"{slug}_xerozify_{version}.{ext}"
            files = {"file": (filename, content_str, mime_type)}

            if game["webhook"]:
                requests.post(game["webhook"], data={"payload_json": json.dumps(payload)}, files=files, timeout=15)
            state[state_key] = version
            updated = True
            updated_summary.append(f"**{game['label']}** (`xerozify.xyz` · `{version}`)")
        else:
            print(f"[xerozify:{slug}] No changes.")
    except Exception as e:
        print(f"[xerozify:{slug}] Error: {e}")

# 4. Send scan summary to the announcements channel on every run
if ANNOUNCEMENTS_WEBHOOK and ANNOUNCEMENTS_WEBHOOK.startswith("http"):
    if updated_summary:
        games_text = "\n".join(f"• {item}" for item in updated_summary)
        desc = f"**🕒 Scan time:** `{search_time}`\n\n**📦 Updated games ({len(updated_summary)}):**\n{games_text}"
        embed_color = 0x2ECC71
    else:
        desc = f"**🕒 Scan time:** `{search_time}`\n\n• Scan completed. No new updates."
        embed_color = 0x95A5A6

    summary_embed = {
        "title": "📢 Offset Scan Log",
        "description": desc,
        "color": embed_color,
        "footer": {"text": "24/7 Monitor · 19 sources checked"}
    }
    try:
        r = requests.post(ANNOUNCEMENTS_WEBHOOK, json={"embeds": [summary_embed]}, timeout=15)
        print(f"[announcements] Sent (HTTP {r.status_code})")
    except Exception as e:
        print(f"[announcements] Error sending summary: {e}")

if updated:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
