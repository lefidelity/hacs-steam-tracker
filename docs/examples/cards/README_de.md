# Lovelace card examples

Below you’ll find a collection of example Lovelace cards for all sensors provided by the Steam Tracker integration.
These examples are meant to help you quickly visualize your Steam data in Home Assistant and can be copied or adapted directly for your own dashboard setup.

> If you want to use these examples out of the box you should use the default "Steam Tracker" as the friendly name.

### Account information

Needed additional integrations:
- [button-card](https://github.com/custom-cards/button-card)
- [entity-progress-card](https://github.com/t1m0thyj/entity-progress-card)

YAML code:
```yaml
type: horizontal-stack
cards:
  - type: custom:button-card
    entity: sensor.steam_tracker_status
    show_name: false
    show_state: false
    show_label: false
    show_entity_picture: true
    entity_picture: |
      [[[ return states['sensor.steam_tracker_status'].attributes.avatar; ]]]
    styles:
      card:
        - border-radius: 50%
        - width: 120px
        - height: 120px
        - padding: 0px
      entity_picture:
        - border-radius: 50%
        - width: 120px
        - height: 120px
  - type: vertical-stack
    cards:
      - type: markdown
        content: >-
          {% set status = states('sensor.steam_tracker_status') %} {% set ts =
          state_attr('sensor.steam_tracker_status','lastlogoff') | int(0) %} {% set
          dt = (as_timestamp(now()) - ts) | int %} {% set days = (dt // 86400)
          %} {% set hours = (dt % 86400 // 3600) %} {% set minutes = (dt % 3600
          // 60) %}

          {% set xp = state_attr('sensor.steam_tracker_profile','player_xp') | int
          %} {% set to_up =
          state_attr('sensor.steam_tracker_profile','player_xp_needed_to_level_up')
          | int %} {% set end = xp + to_up %}

          **Level {{ states('sensor.steam_tracker_profile') }}** <small> | XP: {{
          "{:,.0f}".format(xp).replace(",", ".") }}</small>
        text_only: true
      - type: custom:entity-progress-card-template
        entity: sensor.steam_tracker_profile
        name: Nächster Aufstieg
        hide:
          - icon
        min_value: 0
        max_value: 100
        percent: >
          {% set xp = state_attr('sensor.steam_tracker_profile', 'player_xp') |
          int(0) %}

          {% set need = state_attr('sensor.steam_tracker_profile',
          'player_xp_needed_to_level_up') | int(0) %}

          {% set minXP = state_attr('sensor.steam_tracker_profile',
          'player_xp_needed_current_level') | int(0) %}

          {% set total = (xp + need) - minXP %}

          {% set progress = xp - minXP %}

          {% if total > 0 %}
            {{ ((progress / total) * 100) | round(0) }}
          {% else %}
            0
          {% endif %}
        secondary: >
          {% set xp = state_attr('sensor.steam_tracker_profile', 'player_xp') |
          int(0) %}

          {% set need = state_attr('sensor.steam_tracker_profile',
          'player_xp_needed_to_level_up') | int(0) %}

          {% set minXP = state_attr('sensor.steam_tracker_profile',
          'player_xp_needed_current_level') | int(0) %}

          {% set progress = xp - minXP %}

          {% set span = (xp+(need))-minXP %}

          {{ progress }} / {{ span }} XP
        bar_color: "#2196f3"
        decimal: 0
        card_mod:
          class: flat
      - type: markdown
        content: >-
          {% set status = states('sensor.steam_tracker_status') %} {% set ts =
          state_attr('sensor.steam_tracker_status','lastlogoff') | int(0) %} {% set
          dt = (as_timestamp(now()) - ts) | int %} {% set days = (dt // 86400)
          %} {% set hours = (dt % 86400 // 3600) %} {% set minutes = (dt % 3600
          // 60) %}

          {% set xp = state_attr('sensor.steam_tracker_profile','player_xp') | int
          %} {% set to_up =
          state_attr('sensor.steam_tracker_profile','player_xp_needed_to_level_up')
          | int %} {% set end = xp + to_up %}


          Status: {{ status }}{% if status == "Offline" %}<small>{% if days > 0
          %}
            Zuletzt online vor {{ days }} Tagen
            {% elif hours > 0 %}
            Zuletzt online vor {{ hours }} Stunden
            {% elif minutes > 0 %}
            Zuletzt online vor {{ minutes }} Minuten
            {% else %}
            Gerade eben online
            {% endif %}
          {% endif %}</small>
        text_only: true
```
---
### Currently played game

Will only be shown, if a game is currently played (the game sensor is not empty).

Needed additional integrations: none

YAML code:
```yaml
type: markdown
content: >-
  &nbsp;

  # Aktuelles Spiel

  {% if states('sensor.steam_tracker_game') == "none" %}

  🎮 Keines

  {% else %}

  ![Logo]({{ state_attr('sensor.steam_tracker_game','logo') }})

  <small>Gesamtspielzeit: {{
  state_attr('sensor.steam_tracker_game','total_playtime_hours') or 0 }} h</small>

  {% endif %}
text_only: true
visibility:
  - condition: state
    entity: sensor.steam_tracker_game
    state_not: none
```

---

### Recently played games

Needed additional integrations:
- [button-card](https://github.com/custom-cards/button-card)

YAML code:
```yaml
type: custom:button-card
entity: sensor.steam_tracker_recent
show_name: false
show_icon: false
show_state: false
show_label: false
styles:
  card:
    - padding: 10px
    - border-radius: 15px
    - display: block
    - width: 100%
  grid:
    - grid-template-areas: "\"list\""
    - grid-template-columns: 1fr
    - grid-template-rows: 1fr
custom_fields:
  list: |
    [[[
      let recent = states['sensor.steam_tracker_recent'];
      let achiev = states['sensor.steam_tracker_recent_achievements'];
      if (!recent || !recent.attributes || !recent.attributes.recent_games) {
        return "<i>Keine Daten</i>";
      }
      let games = recent.attributes.recent_games.slice(0,3);
      let achievMap = {};
      if (achiev && achiev.attributes && achiev.attributes.recent_achievements) {
        achiev.attributes.recent_achievements.forEach(a => {
          achievMap[a.appid] = a;
        });
      }

      let out = "<div style='display:flex;flex-direction:column;gap:10px;width:100%;'>";
      games.forEach(g => {
        
        // Achievements hinzufügen
        let achievText = "";
        let a = achievMap[g.appid];
        if (a && a.total && a.unlocked !== null) {
          achievText = `🏆 ${a.unlocked}/${a.total} (${Math.round(a.percent)}%)`;
        }

        out += `
          <div style="display:flex;align-items:center;gap:10px;background:var(--ha-card-background,var(--card-background-color));padding:8px;border-radius:10px;width:100%;">
            <img src="${g.logo}" style="max-width:40%;height:auto;border-radius:6px;flex-shrink:0;">
            <div style="flex:1;min-width:0;white-space:normal;word-break:break-word;">
              <div style="font-size:16px;font-weight:bold;">${g.name}</div>
              <div style="font-size:13px;color:var(--secondary-text-color);">
                ⏱ ${Math.round(g.playtime_2weeks_h)}h / ${Math.round(g.playtime_total_h)}h gesamt<br>
                ${achievText}
              </div>
            </div>
          </div>`;
      });
      out += "</div>";
      return out;
    ]]]
```

---

### Library Statistics

Needed additional integrations: none

YAML code:
```yaml
type: markdown
content: |
  &nbsp;
  #  Bibliothek-Statistik
  <table>
    <tr width="70%">
      <td>🎲 Spiele gesamt&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
      <td>{{ '{:,.0f}'.format(state_attr('sensor.steam_tracker_playtime','game_count') or 0).replace(',', '.') }}</td>
    </tr>
    <tr>
      <td>⏱️ Gesamtzeit</td>
      <td>{{ '{:,.0f}'.format(state_attr('sensor.steam_tracker_playtime','total_playtime_hours') or 0).replace(',', '.') }} h</td>
    </tr>
    <tr>
      <td>⏱️ Top 5 Zeit</td>
      <td>{{ '{:,.0f}'.format(state_attr('sensor.steam_tracker_playtime','top_5_playtime_hours') or 0).replace(',', '.') }} h</td>
    </tr>
    <tr>
      <td>😬 Pile of Shame</td>
      <td>
        {% set pile = state_attr('sensor.steam_tracker_playtime','pile_of_shame_count') or 0 %}{% set total = state_attr('sensor.steam_tracker_playtime','game_count') or 1 %}{{ pile }} ({{ ((pile / total) * 100) | round(0) }}%)
      </td>
    </tr>
  </table>
text_only: true
```
---

### Player statistics

Needed additional integrations: none

YAML code:
```yaml
type: markdown
content: |
  &nbsp;
  # Spieler-Statistik
  <table>
    <tr>
      <td>🏆 Errungenschaften gesamt</td>
      <td>
        {{ '{:,.0f}'.format(state_attr('sensor.steam_tracker_global_stats','achievements_total') or 0).replace(',', '.') }}
        /
        {{ '{:,.0f}'.format(state_attr('sensor.steam_tracker_global_stats','achievements_possible') or 0).replace(',', '.') }}
      </td>
    </tr>
    <tr>
      <td>🎯 Perfekte Spiele</td>
      <td>{{ state_attr('sensor.steam_tracker_global_stats','perfect_games') or 0 }}</td>
    </tr>
    <tr>
      <td>📊 Durchsch. Komplettierung&nbsp;&nbsp;&nbsp;&nbsp;</td>
      <td>{{ (state_attr('sensor.steam_tracker_global_stats','avg_completion_rate') or 0) | round(1) }} %</td>
    </tr>
    <tr>
      <td>🎖️ Abzeichen insgesamt</td>
      <td>{{ state_attr('sensor.steam_tracker_global_stats','badge_count') or 0 }}</td>
    </tr>
    <tr>
      <td>🃏 Sammelkarten</td>
      <td>{{ state_attr('sensor.steam_tracker_global_stats','card_badge_count') or 0 }}</td>
    </tr>
  </table>
text_only: true
```


---

### Top-5 Games (Mushroom Template Card)

Needed additional integrations:
- [button-card](https://github.com/custom-cards/button-card)


YAML code:
```yaml
type: custom:button-card
entity: sensor.steam_tracker_playtime
show_name: false
show_icon: false
show_state: false
show_label: false
styles:
  card:
    - padding: 10px
    - border-radius: 15px
    - display: block
    - width: 100%
  grid:
    - grid-template-areas: "\"list\""
    - grid-template-columns: 1fr
    - grid-template-rows: 1fr
custom_fields:
  list: |
    [[[
      let s = states['sensor.steam_tracker_playtime'];
      if (!s || !s.attributes || !s.attributes.top_5_games) {
        return "<i>Keine Daten</i>";
      }
      let games = s.attributes.top_5_games.slice(0,5);
      let out = "<div style='display:flex;flex-direction:column;gap:10px;width:100%;'>";
      games.forEach(g => {
        // Achievements-Text nur, wenn vorhanden
        let achievText = "";
        if (g.achievements_total && g.achievements_unlocked !== null) {
          achievText = `🏆 ${g.achievements_unlocked}/${g.achievements_total} (${Math.round(g.achievements_percent)}%)<br>`;
        }

        out += `
          <div style="display:flex;align-items:center;gap:10px;background:var(--ha-card-background,var(--card-background-color));padding:8px;border-radius:10px;width:100%;">
            <img src="${g.logo}" style="max-width:40%;height:auto;border-radius:6px;flex-shrink:0;">
            <div style="flex:1;min-width:0;white-space:normal;word-break:break-word;">
              <div style="font-size:16px;font-weight:bold;">${g.name}</div>
              <div style="font-size:13px;color:var(--secondary-text-color);">
                ⏱ ${Math.round(g.hours)} h<br>
                ${achievText}
              </div>
            </div>
          </div>`;
      });
      out += "</div>";
      return out;
    ]]]

```

---

### Friends list

Needed additional integrations:
- [button-card](https://github.com/custom-cards/button-card)


YAML code:
```yaml
ttype: custom:button-card
entity: sensor.steam_tracker_friends
show_name: false
show_icon: false
show_state: false
show_label: false
styles:
  card:
    - padding: 10px
    - border-radius: 15px
    - display: block
  grid:
    - grid-template-areas: "\"list\""
    - grid-template-columns: 1fr
    - grid-template-rows: 1fr
custom_fields:
  list: |
    [[[
      let s = states['sensor.steam_tracker_friends'];
      if (!s || !s.attributes || !s.attributes.friends) {
        return "<i>Keine Freunde gefunden</i>";
      }
      let friends = s.attributes.friends;

      // Online zuerst sortieren
      let onlineStates = ["Online", "Busy", "Away", "Snooze", "Looking to play", "Looking to trade"];
      friends.sort((a, b) => {
        let aOnline = onlineStates.includes(a.status);
        let bOnline = onlineStates.includes(b.status);
        if (aOnline && !bOnline) return -1;
        if (!aOnline && bOnline) return 1;
        return a.personaname.localeCompare(b.personaname);
      });

      let out = "<div style='display:flex;flex-direction:column;gap:10px;width:100%;'>";
      friends.forEach(f => {
        let game = f.game ? `<br>🎮 ${f.game}` : "";
        out += `
          <div style="display:flex;align-items:center;gap:12px;padding:8px;background:var(--ha-card-background,var(--card-background-color));border-radius:10px;width:100%;">
            <img src="${f.avatar}" style="width:50px;height:50px;border-radius:50%;flex-shrink:0;">
            <div style="flex:1;min-width:0;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">
              <div style="font-size:16px;font-weight:bold;">${f.personaname}</div>
              <div style="font-size:13px;color:var(--secondary-text-color);">
                ${f.status} ${game}
              </div>
            </div>
          </div>`;
      });
      out += "</div>";
      return out;
    ]]]
```

---

### Games overview

Needed additional integrations:
- [flex-table-card](https://github.com/custom-cards/flex-table-card)


YAML code:
```yaml
type: custom:flex-table-card
entities:
  include: sensor.steam_tracker_playtime
columns:
  - name: Spiel
    data: all_games.name
    align: start
  - name: Stunden
    data: all_games.hours
    align: end
css:
  tbody tr:nth-child(odd): "background-color: #faf8ff !important"
  tbody tr:nth-child(even): "background-color: #f4f3fa !important"
  thead th: "background-color: #eeeeee; font-weight: bold; padding: 8px; text-align: left"
  tbody td: "padding: 8px"
  thead th:nth-child(2): "text-align: right"
  tbody td:nth-child(2): "text-align: right"
  tbody tr:hover: "background-color: #dbeeff !important"
```