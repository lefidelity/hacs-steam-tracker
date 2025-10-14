# Steam Tracker for Home Assistant

A Home Assistant custom integration that talks to the Steam Web API and exposes rich account and game telemetry as sensors. Keep an eye on your online status, the game you are playing, accumulated playtime, recent achievements, friends list, and more.

> Not affiliated with Valve or Steam. Use at your own risk.

---

## Features

- Player status: presence, avatar, profile link, timestamps
- Current game: title, app id, header art, total hours played
- Playtime summary: global totals, top five games, achievement progress
- Recently played: activity in the last two weeks with last played timestamp
- Recent achievements: unlocked versus total per game
- Global stats: completion ratios, badge counts, perfect games
- Friends: list of friends, their presence, and currently played titles

---

## Installation

### HACS (Recommended)
1. Open **HACS -> Integrations**.
2. Use the search bar to find **Steam Tracker** and install it.

Or click the badge below to open the repository page directly inside HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=lefidelity&repository=hacs-steam-tracker&category=integration)

After installation, restart Home Assistant once to load the integration.

### HACS (Manual Repository)
1. Open **HACS -> Integrations**.
2. Click the menu (three dots) in the top right and choose **Custom repositories**.
3. Paste `https://github.com/lefidelity/hacs-steam-tracker` and select **Integration**.
4. Click **Add**, then search for **Steam Tracker** and install it.
5. Restart Home Assistant.

### Manual Installation
1. Download the latest release and copy `custom_components/steam_tracker` into your Home Assistant configuration directory:
   ```
   config/custom_components/steam_tracker
   ```
2. Restart Home Assistant.

---

## Configuration

Everything can be configured in the UI:

1. Navigate to **Settings -> Devices & Services -> Add Integration**.
2. Search for **Steam Tracker**.
3. Provide your **Steam User ID**, **Steam Web API key**, and a friendly **integration name**.

The integration creates sensors automatically with names based on the title you choose.

Already using `configuration.yaml`? Leave your existing entry in place for the first restart so Home Assistant can import it into the UI, then remove the YAML.

### Legacy YAML (optional)

```yaml
sensor:
  - platform: steam_tracker
    api_key: !secret steam_api_key
    steam_id: "7656119XXXXXXXXXX"
    name: "Steam Tracker"
```

### Entity IDs

Home Assistant slugifies the integration name. With the default `Steam Tracker` you will see:

- `sensor.steam_tracker_status`
- `sensor.steam_tracker_game`
- `sensor.steam_tracker_playtime`
- `sensor.steam_tracker_profile`
- `sensor.steam_tracker_recent`
- `sensor.steam_tracker_recent_achievements`
- `sensor.steam_tracker_global_stats`
- `sensor.steam_tracker_friends`

Renaming the integration (e.g., `Mein Steam Game`) produces matching entity IDs such as `sensor.mein_steam_game_game`.

---

## Provided Sensors and Attributes

### `sensor.*_status`
- **State**: `Offline | Online | Busy | Away | Snooze | Looking to trade | Looking to play | Unknown`
- **Attributes**: `personaname`, `profileurl`, `avatar`, `lastlogoff`

### `sensor.*_game`
- **State**: current game title or `none`
- **Attributes**: `gameid`, `name`, `personaname`, `logo`, `total_playtime_hours`

### `sensor.*_playtime`
- **State**: total playtime across all games (hours)
- **Attributes**: `top_5_games`, `all_games`, `game_count`, `total_playtime_hours`, `top_5_playtime_hours`, `playtime_by_gameid`, `pile_of_shame_count`

### `sensor.*_profile`
- **State**: Steam player level
- **Attributes**: `player_xp`, `player_xp_needed_to_level_up`, `player_xp_needed_current_level`

### `sensor.*_recent`
- **State**: most recent game or `none`
- **Attributes**: `recent_games` (list with `appid`, `name`, `playtime_2weeks_h`, `playtime_total_h`, `logo`, `last_played`), `game_count`

### `sensor.*_recent_achievements`
- **State**: number of games with achievement data
- **Attributes**: `recent_achievements` (list with `appid`, `name`, `unlocked`, `total`, `percent`, `logo`)

### `sensor.*_global_stats`
- **State**: total unlocked achievements
- **Attributes**: `achievements_total`, `achievements_possible`, `perfect_games`, `avg_completion_rate`, `badge_count`, `card_badge_count`

### `sensor.*_friends`
- **State**: number of Steam friends
- **Attributes**: `friends` (list with `steamid`, `personaname`, `avatar`, `profileurl`, `status`, `game`)

---

## Lovelace Examples

### Top-5 Games (Mushroom Template Card)
```yaml
type: custom:mushroom-template-card
primary: >
  {{ state_attr('sensor.steam_tracker_playtime', 'top_5_games')[0]['name'] }}
secondary: >
  {{ state_attr('sensor.steam_tracker_playtime', 'top_5_games')[0]['hours'] }} h
  • {{ state_attr('sensor.steam_tracker_playtime', 'top_5_games')[0]['achievements_unlocked'] }}/{{ state_attr('sensor.steam_tracker_playtime', 'top_5_games')[0]['achievements_total'] }}
  ({{ state_attr('sensor.steam_tracker_playtime', 'top_5_games')[0]['achievements_percent'] }}%)
entity: sensor.steam_tracker_playtime
icon: mdi:steam
```

### Recent Games (Markdown)
```yaml
type: markdown
content: >
  {% set games = state_attr('sensor.steam_tracker_recent', 'recent_games') %}
  {% if games and games | count > 0 %}
  **Last played:** {{ games[0]['name'] }}  
  {{ as_datetime(games[0]['last_played']) | as_local | timestamp_custom('%Y-%m-%d %H:%M') }}
  {% else %}
  _No recent games_
  {% endif %}
```

---

## Update Intervals

- Status: 1 minute
- Game: 5 minutes
- Recent games: 10 minutes
- Playtime, profile, recent achievements: 3 hours
- Global stats: 5 hours
- Friends: 5 minutes

Each sensor defines its own `SCAN_INTERVAL`.

---

## Local Testing

1. Copy `custom_components/steam_tracker` into your Home Assistant config.
2. Restart Home Assistant.
3. Add the integration via **Settings -> Devices & Services -> Add Integration**.
4. Inspect the new sensors under **Developer Tools -> States**.

---

## Troubleshooting

- **No playtime on `sensor.*_game`**: make sure the account is currently in-game; data comes from `GetOwnedGames`.
- **`last_played` looks numeric**: it is a Unix timestamp; use a template to format it.
- **Unexpected entity IDs**: confirm the actual names in **Developer Tools -> States**.
- **Verbose logging**:
  ```yaml
  logger:
    default: warning
    logs:
      custom_components.steam_tracker: debug
  ```

---

## Privacy

- Secrets stay local to your Home Assistant instance.
- Only public Steam Web APIs are used.
- Never commit API keys or Steam IDs to source control.

---

## Roadmap

- Options flow for scan interval tuning
- Per-sensor enable/disable toggles
- Game-specific icons or images
- Additional translations
- Automated tests and CI

---

## Contributing

Pull requests and issues are welcome. Please include:
- Steps to reproduce
- Home Assistant version
- Relevant logs (`custom_components.steam_tracker: debug`)
- Expected versus actual behavior

---

## License

MIT

---

## Changelog

**0.1.0**
- Initial release
- `sensor.*_game` exposes `total_playtime_hours`
- Top-5 list includes achievement counts and percentage
- Recently played sensor exposes `last_played` timestamp
