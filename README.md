# Steam Tracker for Home Assistant

A **Home Assistant custom integration** that connects to the **Steam Web API** and exposes rich player and game stats as sensors.
Track your current status, playtime (total and per game), Top-5 games (with achievements), recently played games (with last played timestamp), global completion stats, and your friends' activity.

> _Not affiliated with Valve or Steam. Use at your own risk._

---

## Features

- **Player status**: online state, current game, avatar, profile link
- **Current game**: game name, app id, header image, **total playtime (hours)** pulled directly via API
- **Playtime summary**: total hours, Top-5 games (hours + achievements), all games list, handy aggregates
- **Recently played**: last 2-week hours, total hours, **last played (Unix timestamp)**
- **Recent achievements**: unlocked/total/percent per recently played game
- **Global stats**: total vs. possible achievements, perfect games, average completion rate, badges
- **Friends**: count, persona name, status, current game, profile

_Add the sensors to Lovelace (Mushroom or stock cards) for a neat dashboard._

---

## Installation

### Option A: HACS (Custom Repository)
1. Open **HACS → Integrations → Custom repositories**
2. Add your repository URL and select **Integration**
3. Search for **Steam Tracker** in HACS and **Install**
4. **Restart Home Assistant**

> Screenshot placeholder: docs/screenshot-hacs-add-repo.png

### Option B: Manual
1. Copy the folder custom_components/steam_tracker into your Home Assistant config:
   `
   config/custom_components/steam_tracker
   `
2. **Restart Home Assistant**

---

## Configuration

Configure everything directly in the Home Assistant UI:

1. Open **Settings → Devices & Services → Add Integration**.
2. Search for **Steam Tracker**.
3. Enter your **Steam User ID**, **Steam Web API key**, and choose an **integration name**.

That's it—the integration creates all entities automatically with a prefix based on the name you provide.

> Already using configuration.yaml? Leave the YAML block in place for the first restart so Home Assistant can import it into the UI. Afterwards you can remove it.

### Legacy YAML (optional)

`yaml
sensor:
  - platform: steam_tracker
    api_key: !secret steam_api_key
    steam_id: "7656119XXXXXXXXXX"
    name: "Steam Tracker"
`

> Screenshot placeholder: docs/screenshot-steam-key-and-id.png

### Entity IDs

Home Assistant converts the integration name into a slug. With the default Steam Tracker you get:

- sensor.steam_tracker_status
- sensor.steam_tracker_game
- sensor.steam_tracker_playtime
- sensor.steam_tracker_profile
- sensor.steam_tracker_recent
- sensor.steam_tracker_recent_achievements
- sensor.steam_tracker_global_stats
- sensor.steam_tracker_friends

If you choose Mein Steam Game as the integration name, you'll see entities like sensor.mein_steam_game_playtime, sensor.mein_steam_game_game, and so on.

---

## Provided Sensors and Attributes

### sensor.*_status
**State**: Offline | Online | Busy | Away | Snooze | Looking to trade | Looking to play | Unknown

**Attributes**:
- personaname
- profileurl
- vatar
- lastlogoff

### sensor.*_game
Shows the **current game** (or 
one).

**Attributes**:
- gameid (appid)
- 
ame
- personaname
- logo (Steam header image)
- 	otal_playtime_hours (fetched directly via GetOwnedGames)

### sensor.*_playtime
**State**: total hours played (all games).

**Attributes**:
- 	op_5_games: list with ppid, 
ame, hours, logo, chievements_unlocked, chievements_total, chievements_percent
- ll_games: list of { name, hours }
- game_count
- 	otal_playtime_hours
- 	op_5_playtime_hours
- playtime_by_gameid (dictionary: ppid -> hours)
- pile_of_shame_count (games < 60 minutes)

### sensor.*_profile
**State**: Steam player level.

**Attributes**:
- player_xp
- player_xp_needed_to_level_up
- player_xp_needed_current_level

### sensor.*_recent
Recently played games (up to 5).

**State**: name of the most recent game, or 
one.

**Attributes**:
- ecent_games: list with ppid, 
ame, playtime_2weeks_h, playtime_total_h, logo, last_played
- game_count

### sensor.*_recent_achievements
**State**: number of games with data.

**Attributes**:
- ecent_achievements: list with ppid, 
ame, unlocked, 	otal, percent, logo

### sensor.*_global_stats
**State**: total unlocked achievements (sum).

**Attributes**:
- chievements_total
- chievements_possible
- perfect_games
- vg_completion_rate (average across games with achievements)
- adge_count
- card_badge_count

### sensor.*_friends
**State**: total number of friends.

**Attributes**:
- riends: list with steamid, personaname, vatar, profileurl, status, game

---

## Lovelace Examples

> Screenshot placeholders: docs/screenshot-overview.png, docs/screenshot-top5.png, docs/screenshot-recent.png, docs/screenshot-friends.png

### Top-5 (Mushroom Template Card)
Requires [Mushroom] installed via HACS.

`yaml
type: custom:mushroom-template-card
primary: >
  {{ state_attr('sensor.steam_tracker_playtime', 'top_5_games')[0]['name'] }}
secondary: >
  {{ state_attr('sensor.steam_tracker_playtime', 'top_5_games')[0]['hours'] }} h ·
  {{ state_attr('sensor.steam_tracker_playtime', 'top_5_games')[0]['achievements_unlocked'] }}/{{ state_attr('sensor.steam_tracker_playtime', 'top_5_games')[0]['achievements_total'] }}
  ({{ state_attr('sensor.steam_tracker_playtime', 'top_5_games')[0]['achievements_percent'] }}%)
entity: sensor.steam_tracker_playtime
icon: mdi:steam
`

### Recent Games (Entity List)
`yaml
type: custom:auto-entities
card:
  type: entities
  title: Recently Played
filter:
  template: |
    {% for game in state_attr('sensor.steam_tracker_recent', 'recent_games') %}
      {{ {'entity': 'sensor.steam_tracker_recent', 'attribute': 'recent_games', 'index': loop.index0, 'name': game.name} | tojson }}
    {% endfor %}
`

### Raw Attribute Table
`yaml
type: entities
title: Steam Tracker (raw)
entities:
  - entity: sensor.steam_tracker_playtime
    attribute: top_5_games
    name: Top 5 games
  - entity: sensor.steam_tracker_recent
    attribute: recent_games
    name: Games (last 2 weeks)
`

### Last Played (formatted)
`yaml
type: markdown
content: >
  {% set games = state_attr('sensor.steam_tracker_recent', 'recent_games') %}
  {% if games and games | count > 0 %}
  **Last played:** {{ games[0]['name'] }}
  {{ as_datetime(games[0]['last_played']) | as_local | timestamp_custom('%Y-%m-%d %H:%M') }}
  {% else %}
  _No recent games_
  {% endif %}
`

### Current Game (with total hours)
`yaml
type: entities
title: Now Playing
entities:
  - entity: sensor.steam_tracker_game
    name: Current game
  - type: attribute
    entity: sensor.steam_tracker_game
    attribute: total_playtime_hours
    name: Total hours (this game)
`

---

## Update Intervals (default)

- Status: every **1 minute**
- Game: every **5 minutes**
- Recent games: every **10 minutes**
- Playtime / Profile / Recent achievements: every **3 hours**
- Global stats: every **5 hours**
- Friends: every **5 minutes**

*(Each sensor defines SCAN_INTERVAL individually.)*

---

## Local Testing

1. Copy custom_components/steam_tracker to your Home Assistant config at:
   `
   config/custom_components/steam_tracker
   `
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration** and pick **Steam Tracker**.
4. Enter your Steam credentials when prompted and verify the new sensors under **Developer Tools → States**.

> Screenshot placeholder: docs/screenshot-ha-states.png

---

## Troubleshooting

- **No playtime on sensor.*_game** – Ensure you're actually in-game; playtime is fetched via GetOwnedGames by ppid.
- **last_played looks like a number** – That's expected: it is a Unix timestamp. Use a template (see Last Played example) for formatting.
- **Rate limits or intermittent data** – Steam APIs can throttle or return partial data.
- **Unexpected entity IDs** – Check **Developer Tools → States** for the actual entity id.
- **Verbose logging**:
  `yaml
  logger:
    default: warning
    logs:
      custom_components.steam_tracker: debug
  `

---

## Privacy

- Your API key and SteamID stay local in Home Assistant.
- The integration fetches data from public Steam Web APIs.
- Do **not** commit secrets to your repository.

---

## Roadmap

- Options flow (tuning intervals, counting rules)
- Selective sensor enable/disable
- Entity pictures or icons per game
- Translations
- Tests and CI

---

## Contributing

PRs and issues are welcome! Please include:
- Reproduction steps
- Home Assistant version
- Logs (with custom_components.steam_tracker: debug)
- Expected vs. actual behavior

---

## License

MIT

---

## Changelog

**0.1.0**
- Initial release
- Game sensor fetches **total_playtime_hours** directly via API
- Top-5 games include achievements X/Y (Z%)
- Recently played exposes last_played (Unix timestamp)
