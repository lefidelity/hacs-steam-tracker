# Steam Tracker for Home Assistant

A **Home Assistant custom integration** that connects to the **Steam Web API** and exposes rich player & game stats as sensors.  
Track your current status, playtime (total & per game), Top-5 games (with achievements), recently played games (with last played timestamp), global completion stats, and your friends’ activity.

> _Not affiliated with Valve or Steam. Use at your own risk._

---

## ✨ Features

- **Player status**: online state, current game, avatar, profile link  
- **Current game**: game name, app id, header image, **total playtime (hours)** pulled directly via API  
- **Playtime summary**: total hours, Top-5 games (hours + achievements), all games list, handy aggregates  
- **Recently played**: last 2-week hours, total hours, **last played (unix timestamp)**  
- **Recent achievements**: unlocked/total/percent per recently played game  
- **Global stats**: total vs. possible achievements, perfect games, average completion rate, badges  
- **Friends**: count, persona name, status, current game, profile  

_💡 Add these sensors to Lovelace (Mushroom or stock cards) for a neat dashboard._

---

## 📦 Installation

### Option A: HACS (Custom Repository)
1. Open **HACS → Integrations → ⋯ → Custom repositories**
2. Add your repository URL and select **Integration**
3. Search for **Steam Tracker** in HACS and **Install**
4. **Restart Home Assistant**

> _Screenshot placeholder: “HACS → Add custom repository”_  
> `docs/screenshot-hacs-add-repo.png`

### Option B: Manual
1. Copy the folder `custom_components/steam_tracker` into your Home Assistant config:
   ```
   config/custom_components/steam_tracker
   ```
2. **Restart Home Assistant**

---

## ⚙️ Configuration

Add to your `configuration.yaml`:

```yaml
sensor:
  - platform: steam_tracker
    api_key: !secret steam_api_key
    steam_id: "7656119XXXXXXXXXX"
    name: "Steam Tracker"
```

**Parameters**
- `api_key` (required): Your Steam Web API key  
- `steam_id` (required): Your 64-bit SteamID (not vanity name)  
- `name` (optional): Prefix for entity names (default: `Steam Tracker`)

> _Screenshot placeholder: “Where to find Steam Web API key & SteamID64”_  
> `docs/screenshot-steam-key-and-id.png`

**Entity IDs**  
Home Assistant converts the `name` into a slug. For example, with `name: Steam Tracker`:

- `sensor.steam_tracker_status`  
- `sensor.steam_tracker_game`  
- `sensor.steam_tracker_playtime`  
- `sensor.steam_tracker_profile`  
- `sensor.steam_tracker_recent`  
- `sensor.steam_tracker_recent_achievements`  
- `sensor.steam_tracker_global_stats`  
- `sensor.steam_tracker_friends`

If you set `name: Mein Steam Game`, you’ll see entities like `sensor.mein_steam_game_playtime`, `sensor.mein_steam_game_game`, etc.

---

## 🧩 Provided Sensors & Attributes

### 1) `sensor.*_status`
**State**: `Offline | Online | Busy | Away | Snooze | Looking to trade | Looking to play | Unknown`  
**Attributes**:  
- `personaname`, `profileurl`, `avatar`, `lastlogoff`

### 2) `sensor.*_game`
Shows the **current game** (or `none`)  
**Attributes**:  
- `gameid` (appid), `name`, `personaname`, `logo` (Steam header image)  
- `total_playtime_hours` ✨ (fetched directly via `GetOwnedGames`)  

### 3) `sensor.*_playtime`
**State**: total hours played (all games)  
**Attributes**:  
- `top_5_games`: list of objects  
  - `appid`, `name`, `hours`, `logo`  
  - `achievements_unlocked`, `achievements_total`, `achievements_percent`  
- `all_games`: list of `{ name, hours }`  
- `game_count`, `total_playtime_hours`, `top_5_playtime_hours`  
- `playtime_by_gameid` (dict: `appid → hours`)  
- `pile_of_shame_count` (games < 60 min)  

### 4) `sensor.*_profile`
**State**: Steam player level  
**Attributes**:  
- `player_xp`, `player_xp_needed_to_level_up`, `player_xp_needed_current_level`

### 5) `sensor.*_recent`
Recently played games (up to 5)  
**State**: name of the most recent game, or `none`  
**Attributes**:  
- `recent_games`: list of objects  
  - `appid`, `name`, `playtime_2weeks_h`, `playtime_total_h`, `logo`  
  - `last_played` (unix timestamp) ✅  
- `game_count`

### 6) `sensor.*_recent_achievements`
**State**: number of games with data  
**Attributes**:  
- `recent_achievements`: list of objects  
  - `appid`, `name`, `unlocked`, `total`, `percent`, `logo`

### 7) `sensor.*_global_stats`
**State**: total unlocked achievements (sum)  
**Attributes**:  
- `achievements_total`, `achievements_possible`, `perfect_games`  
- `avg_completion_rate` (avg across games with achievements)  
- `badge_count`, `card_badge_count`

### 8) `sensor.*_friends`
**State**: total number of friends  
**Attributes**:  
- `friends`: list of objects  
  - `steamid`, `personaname`, `avatar`, `profileurl`, `status`, `game`

---

## 🖼️ Lovelace Examples

> _Screenshot placeholders_  
> `docs/screenshot-overview.png` — Dashboard overview  
> `docs/screenshot-top5.png` — Top-5 with achievements  
> `docs/screenshot-recent.png` — Recently played  
> `docs/screenshot-friends.png` — Friends activity

### Top-5 (Mushroom Template Card)
Requires [Mushroom] installed via HACS.

```yaml
type: custom:mushroom-template-card
primary: >
  {{ state_attr('sensor.steam_tracker_playtime', 'top_5_games')[0]['name'] }}
secondary: >
  {{ state_attr('sensor.steam_tracker_playtime', 'top_5_games')[0]['hours'] }} h ·
  {{ state_attr('sensor.steam_tracker_playtime', 'top_5_games')[0]['achievements_unlocked'] }}/{{ state_attr('sensor.steam_tracker_playtime', 'top_5_games')[0]['achievements_total'] }}
  ({{ state_attr('sensor.steam_tracker_playtime', 'top_5_games')[0]['achievements_percent'] }}%)
entity: sensor.steam_tracker_playtime
icon: mdi:steam
```

Duplicate for indices `[1]…[4]` for a full Top-5 grid.

### Recently Played (Entities)
```yaml
type: entities
title: Recently Played
entities:
  - type: attribute
    entity: sensor.steam_tracker_recent
    attribute: recent_games
    name: Games (last 2 weeks)
```

### Last Played (formatted)
```yaml
type: markdown
content: >
  {% set g = state_attr('sensor.steam_tracker_recent', 'recent_games') %}
  {% if g and g | count > 0 %}
  **Last played:** {{ g[0]['name'] }} –
  {{ as_datetime(g[0]['last_played']) | as_local | timestamp_custom('%Y-%m-%d %H:%M') }}
  {% else %}
  _No recent games_
  {% endif %}
```

### Current Game (with total hours)
```yaml
type: entities
title: Now Playing
entities:
  - entity: sensor.steam_tracker_game
    name: Current game
  - type: attribute
    entity: sensor.steam_tracker_game
    attribute: total_playtime_hours
    name: Total hours (this game)
```

---

## 🔍 Update Intervals (default)

- Status: every **1 min**  
- Game: every **5 min**  
- Recent games: every **10 min**  
- Playtime / Profile / Recent achievements: every **3 h**  
- Global stats: every **5 h**  
- Friends: every **5 min**

*(These are implemented as class-level `SCAN_INTERVAL`s.)*

---

## 🧪 Local Testing

1. Copy `custom_components/steam_tracker` to your HA config at:
   ```
   config/custom_components/steam_tracker
   ```
2. Add the YAML config (see above)  
3. **Restart Home Assistant**  
4. Open **Developer Tools → States** and search for `sensor.steam_tracker_*`

> _Screenshot placeholder: “Developer Tools → States”_  
> `docs/screenshot-ha-states.png`

---

## 🛠️ Troubleshooting

- **No playtime on `sensor.*_game`**  
  Ensure you’re actually in-game; playtime is fetched via `GetOwnedGames` by `appid`.  

- **`last_played` appears numeric**  
  That’s expected: it’s a unix timestamp. Use a template (see **Last Played (formatted)**).  

- **Rate limits / intermittent data**  
  Steam APIs can throttle or return partial data.  

- **Wrong entity IDs**  
  Check **Developer Tools → States** for the actual entity id.  

- **Logging**
  ```yaml
  logger:
    default: warning
    logs:
      custom_components.steam_tracker: debug
  ```

---

## 🔐 Privacy

- Your API key and SteamID stay local in Home Assistant.  
- The integration fetches data from public Steam Web APIs.  
- Do **not** commit secrets to your repository.  

---

## 🗺️ Roadmap

- Config Flow (UI setup)  
- Options (tuning intervals, counting rules)  
- Entity pictures / icons per game  
- Translations  
- Tests & CI  

---

## 🤝 Contributing

PRs and issues are welcome!  
Please include:
- Repro steps  
- HA version  
- Logs (with `custom_components.steam_tracker: debug`)  
- Expected vs. actual behavior  

---

## 📄 License

MIT (recommended for community contributions)

---

## 🧾 Changelog

**0.1.0**
- Initial release  
- `Game` sensor fetches **total_playtime_hours** directly via API  
- Top-5 games include achievements X/Y (Z%)  
- Recently played exposes `last_played` (unix timestamp)  
