# Integration to get steam account information 
import logging
import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_API_KEY, CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

CONF_STEAM_ID = "steam_id"

DEFAULT_NAME = "Steam Tracker"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_STEAM_ID): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

API_URL = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up Steam Tracker sensors."""
    api_key = config[CONF_API_KEY]
    steam_id = config[CONF_STEAM_ID]
    name = config[CONF_NAME]

    add_entities([
        SteamStatusSensor(api_key, steam_id, f"{name} Status"),
        SteamGameSensor(api_key, steam_id, f"{name} Game"),
        SteamPlaytimeSensor(api_key, steam_id, f"{name} Playtime"),
        SteamProfileSensor(api_key, steam_id, f"{name} Profile"),
        SteamRecentGamesSensor(api_key, steam_id, f"{name} Recent"),
        SteamRecentAchievementsSensor(api_key, steam_id, f"{name} Recent Achievements"),
        SteamGlobalStatsSensor(api_key, steam_id, f"{name} Global Stats"),
        SteamFriendsSensor(api_key, steam_id, f"{name} Friends"),
    ])


class SteamBaseSensor(Entity):
    """Base class for Steam Tracker sensors."""

    def __init__(self, api_key, steam_id, name):
        self._api_key = api_key
        self._steam_id = steam_id
        self._name = name
        self._state = None
        self._attrs = {}

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attrs

    def update(self):
        """Fetch data from Steam API."""
        try:
            params = {"key": self._api_key, "steamids": self._steam_id}
            response = requests.get(API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()["response"]["players"][0]
            self.parse_data(data)
        except Exception as e:
            _LOGGER.error("Error fetching data from Steam: %s", e)


class SteamStatusSensor(SteamBaseSensor):
    """Shows online status of the player."""
    SCAN_INTERVAL = timedelta(minutes=1)
    
    def parse_data(self, data):
        state_map = {
            0: "Offline",
            1: "Online",
            2: "Busy",
            3: "Away",
            4: "Snooze",
            5: "Looking to trade",
            6: "Looking to play",
        }
        self._state = state_map.get(data.get("personastate", 0), "Unknown")
        self._attrs = {
            "personaname": data.get("personaname"),
            "profileurl": data.get("profileurl"),
            "avatar": data.get("avatarfull"),
            "lastlogoff": data.get("lastlogoff"),
        }


class SteamGameSensor(SteamBaseSensor):
    """Shows current game being played."""
    SCAN_INTERVAL = timedelta(minutes=5)
    
    def parse_data(self, data):
        current_game = data.get("gameextrainfo")
        if not current_game:
            self._state = "none"
            self._attrs = {}
            return
    
        current_game_id = str(data.get("gameid"))
    
        # standard infos
        self._state = current_game
        self._attrs = {
            "gameid": current_game_id,
            "name": current_game,
            "personaname": data.get("personaname"),
            "logo": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{current_game_id}/header.jpg",
        }
    
        # get overall playtime for current game
        try:
            params = {
                "key": self._api_key,
                "steamid": self._steam_id,
                "include_appinfo": False,
                "include_played_free_games": True,
            }
            resp = requests.get(API_OWNED_GAMES, params=params, timeout=10)
            resp.raise_for_status()
            games = resp.json().get("response", {}).get("games", [])
            for g in games:
                if str(g.get("appid")) == current_game_id:
                    hours = round(g.get("playtime_forever", 0) / 60, 1)
                    self._attrs["total_playtime_hours"] = hours
                    break
        except Exception as e:
            _LOGGER.error("Error fetching playtime for game %s: %s", current_game_id, e)


API_OWNED_GAMES = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"

class SteamPlaytimeSensor(SteamBaseSensor):
    """Shows total playtime and top 5 games."""
    SCAN_INTERVAL = timedelta(hours=3)

    def update(self):
        """Fetch owned games and playtime data from Steam API."""
        try:
            params = {
                "key": self._api_key,
                "steamid": self._steam_id,
                "include_appinfo": True,   # liefert Namen der Spiele
                "include_played_free_games": True
            }
            response = requests.get(API_OWNED_GAMES, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()["response"]

            games = data.get("games", [])
            if not games:
                self._state = 0
                self._attrs = {"top_5_games": []}
                return

            # overall playtime in hours
            total_minutes = sum(g.get("playtime_forever", 0) for g in games)
            self._state = round(total_minutes / 60, 1)

            # top 5 games according to playtime
            top_games = sorted(
                games,
                key=lambda x: x.get("playtime_forever", 0),
                reverse=True
            )[:5]
            
            # a list of all games with playtime in hours
            all_games = [
                {
                    "name": g.get("name"),
                    "hours": round(g.get("playtime_forever", 0) / 60, 1)
                }
                for g in sorted(games, key=lambda x: x.get("name", ""))
            ]
            
            pile_of_shame = [
                g for g in games if g.get("playtime_forever", 0) < 60
            ]
            
            # overall minues
            total_minutes = sum(g.get("playtime_forever", 0) for g in games)
            total_hours = round(total_minutes / 60, 1)
            
            # top 5 hours
            top_hours = round(sum(g.get("playtime_forever", 0) for g in top_games) / 60, 1)
            
            playtime_by_gameid = {
                str(g["appid"]): round(g.get("playtime_forever", 0) / 60, 1)
                for g in games
            }
            
            top_games_list = []
            for g in top_games:
                appid = g.get("appid")
                name = g.get("name")
                hours = round(g.get("playtime_forever", 0) / 60, 1)
            
                # Default Werte
                unlocked, total, percent = None, None, None
            
                try:
                    # Achievements des Users abrufen
                    user_params = {
                        "key": self._api_key,
                        "steamid": self._steam_id,
                        "appid": appid,
                    }
                    user_resp = requests.get(API_ACHIEVEMENTS, params=user_params, timeout=10)
                    if user_resp.ok:
                        user_data = user_resp.json().get("playerstats", {})
                        achs = user_data.get("achievements", [])
                        unlocked = sum(1 for a in achs if a.get("achieved") == 1)
                        total = len(achs)
                        if total > 0:
                            percent = round((unlocked / total) * 100, 1)
                except Exception:
                    pass
            
                top_games_list.append({
                    "appid": appid,
                    "name": name,
                    "hours": hours,
                    "logo": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg",
                    "achievements_unlocked": unlocked,
                    "achievements_total": total,
                    "achievements_percent": percent,
                })

            
            self._state = total_hours  # overall playtime as state in hours
            self._attrs = {
                "top_5_games": top_games_list,
                "all_games": all_games,
                "game_count": len(games),
                "total_playtime_hours": total_hours,
                "top_5_playtime_hours": top_hours,
                "playtime_by_gameid": playtime_by_gameid,
                "pile_of_shame_count": len(pile_of_shame)
            }

        except Exception as e:
            _LOGGER.error("Error fetching owned games from Steam: %s", e)
            self._state = None
            self._attrs = {}

API_BADGES = "https://api.steampowered.com/IPlayerService/GetBadges/v1/"

class SteamProfileSensor(SteamBaseSensor):
    """Shows profile info like level and XP."""
    
    SCAN_INTERVAL = timedelta(hours=3)
    def update(self):
        try:
            params = {"key": self._api_key, "steamid": self._steam_id}
            response = requests.get(API_BADGES, params=params, timeout=10)
            response.raise_for_status()
            data = response.json().get("response", {})

            self._state = data.get("player_level", 0)
            self._attrs = {
                "player_xp": data.get("player_xp"),
                "player_xp_needed_to_level_up": data.get("player_xp_needed_to_level_up"),
                "player_xp_needed_current_level": data.get("player_xp_needed_current_level"),
            }
        except Exception as e:
            _LOGGER.error("Error fetching profile data from Steam: %s", e)
            self._state = None
            self._attrs = {}

API_RECENT_GAMES = "https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/"

class SteamRecentGamesSensor(SteamBaseSensor):
    """Shows recently played games."""
    SCAN_INTERVAL = timedelta(minutes=10)
    
    def update(self):
        try:
            params = {
                "key": self._api_key,
                "steamid": self._steam_id,
                "count": 5,  # nur die letzten 5 Spiele
            }
            response = requests.get(API_RECENT_GAMES, params=params, timeout=10)
            response.raise_for_status()
            data = response.json().get("response", {})

            games = data.get("games", [])
            if not games:
                self._state = "none"
                self._attrs = {"recent_games": []}
                return

            # Erstes Spiel als State
            first = games[0]
            self._state = first.get("name", "unknown")

            # Spieleliste aufbereiten
            recent_games = [
                {
                    "appid": g.get("appid"),
                    "name": g.get("name"),
                    "playtime_2weeks_h": round(g.get("playtime_2weeks", 0) / 60, 1),
                    "playtime_total_h": round(g.get("playtime_forever", 0) / 60, 1),
                    "logo": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{g.get('appid')}/header.jpg",
                    "last_played": g.get("rtime_last_played")
                }
                for g in games
            ]

            self._attrs = {
                "recent_games": recent_games,
                "game_count": data.get("total_count", 0),
            }

        except Exception as e:
            _LOGGER.error("Error fetching recent games from Steam: %s", e)
            self._state = None
            self._attrs = {}

API_ACHIEVEMENTS = "https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/"
API_SCHEMA = "https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/"
API_RECENT_GAMES = "https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/"

class SteamRecentAchievementsSensor(SteamBaseSensor):
    """Shows achievement progress for recently played games."""
    SCAN_INTERVAL = timedelta(hours=3)

    def update(self):
        try:
            params = {
                "key": self._api_key,
                "steamid": self._steam_id,
                "count": 5,  # only check the last 5 games
            }
            response = requests.get(API_RECENT_GAMES, params=params, timeout=15)
            response.raise_for_status()
            games = response.json().get("response", {}).get("games", [])

            achievements_data = []
            for g in games:
                appid = g.get("appid")
                name = g.get("name")

                # get achievements for user
                user_params = {
                    "key": self._api_key,
                    "steamid": self._steam_id,
                    "appid": appid,
                }
                try:
                    user_resp = requests.get(API_ACHIEVEMENTS, params=user_params, timeout=10)
                    user_resp.raise_for_status()
                    user_data = user_resp.json().get("playerstats", {})
                    unlocked = sum(1 for a in user_data.get("achievements", []) if a.get("achieved") == 1)
                except Exception:
                    unlocked = None

                # get scheme (overall)
                try:
                    schema_resp = requests.get(API_SCHEMA, params={"key": self._api_key, "appid": appid}, timeout=10)
                    schema_resp.raise_for_status()
                    schema_data = schema_resp.json().get("game", {})
                    total = len(schema_data.get("availableGameStats", {}).get("achievements", []))
                except Exception:
                    total = None

                percent = None
                if unlocked is not None and total and total > 0:
                    percent = round((unlocked / total) * 100, 1)

                achievements_data.append({
                    "appid": appid,
                    "name": name,
                    "unlocked": unlocked,
                    "total": total,
                    "percent": percent,
                    "logo": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg",
                })

            self._state = len(achievements_data)  # Anzahl Spiele mit Daten
            self._attrs = {"recent_achievements": achievements_data}

        except Exception as e:
            _LOGGER.error("Error fetching recent achievements: %s", e)
            self._state = None
            self._attrs = {}


API_COMMUNITY = "https://steamcommunity.com/profiles/{steamid}/?xml=1"
API_BADGES = "https://api.steampowered.com/IPlayerService/GetBadges/v1/"

import xml.etree.ElementTree as ET

class SteamGlobalStatsSensor(SteamBaseSensor):
    """Shows global achievement stats (expensive: iterates over all games)."""
    SCAN_INTERVAL = timedelta(hours=5)
    
    def update(self):
        try:
            # 1) Alle Spiele abrufen
            params = {
                "key": self._api_key,
                "steamid": self._steam_id,
                "include_appinfo": True,
                "include_played_free_games": True,
            }
            resp = requests.get(API_OWNED_GAMES, params=params, timeout=30)
            resp.raise_for_status()
            games = resp.json().get("response", {}).get("games", [])

            total_unlocked = 0
            total_possible = 0
            perfect_games = 0
            completion_rates = []

            for g in games:
                appid = g.get("appid")
                if not appid:
                    continue

                # 2) Player Achievements
                try:
                    params = {
                        "key": self._api_key,
                        "steamid": self._steam_id,
                        "appid": appid,
                    }
                    ach_resp = requests.get(API_ACHIEVEMENTS, params=params, timeout=10)
                    if ach_resp.status_code != 200:
                        continue
                    ach_data = ach_resp.json().get("playerstats", {})
                    achs = ach_data.get("achievements", [])
                    unlocked = sum(1 for a in achs if a.get("achieved") == 1)
                    total = len(achs)

                    if total > 0:
                        total_unlocked += unlocked
                        total_possible += total
                        if unlocked == total:
                            perfect_games += 1
                        completion_rates.append(unlocked / total * 100)

                except Exception:
                    continue

            avg_completion = round(sum(completion_rates) / len(completion_rates), 1) if completion_rates else 0

            # 3) Badges abrufen
            badge_params = {"key": self._api_key, "steamid": self._steam_id}
            badge_resp = requests.get(API_BADGES, params=badge_params, timeout=10)
            badge_data = badge_resp.json().get("response", {})
            badges = badge_data.get("badges", [])
            badge_count = len(badges)
            card_badge_count = len([b for b in badges if "appid" in b])

            # 4) Ergebnis
            self._state = total_unlocked
            self._attrs = {
                "achievements_total": total_unlocked,
                "achievements_possible": total_possible,
                "perfect_games": perfect_games,
                "avg_completion_rate": avg_completion,
                "badge_count": badge_count,
                "card_badge_count": card_badge_count,
            }

        except Exception as e:
            _LOGGER.error("Error fetching global stats: %s", e)
            self._state = None
            self._attrs = {}

API_FRIENDS = "https://api.steampowered.com/ISteamUser/GetFriendList/v1/"
API_SUMMARIES = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"

class SteamFriendsSensor(SteamBaseSensor):
    """Shows Steam friends and their current status."""
    SCAN_INTERVAL = timedelta(minutes=5)

    def update(self):
        try:
            # step 1: get friends list
            params = {
                "key": self._api_key,
                "steamid": self._steam_id,
                "relationship": "friend"
            }
            resp = requests.get(API_FRIENDS, params=params, timeout=15)
            resp.raise_for_status()
            friends_data = resp.json().get("friendslist", {}).get("friends", [])

            if not friends_data:
                self._state = 0
                self._attrs = {"friends": []}
                return

            friend_ids = [f["steamid"] for f in friends_data]

            # step 2: get details for friends (max 100 per call)
            friends_info = []
            for i in range(0, len(friend_ids), 100):
                batch_ids = friend_ids[i:i+100]
                params = {"key": self._api_key, "steamids": ",".join(batch_ids)}
                info_resp = requests.get(API_SUMMARIES, params=params, timeout=15)
                info_resp.raise_for_status()
                players = info_resp.json().get("response", {}).get("players", [])
                for p in players:
                    state_map = {
                        0: "Offline",
                        1: "Online",
                        2: "Busy",
                        3: "Away",
                        4: "Snooze",
                        5: "Looking to trade",
                        6: "Looking to play",
                    }
                    friends_info.append({
                        "steamid": p.get("steamid"),
                        "personaname": p.get("personaname"),
                        "avatar": p.get("avatarfull"),
                        "profileurl": p.get("profileurl"),
                        "status": state_map.get(p.get("personastate", 0), "Unknown"),
                        "game": p.get("gameextrainfo"),
                    })

            self._state = len(friends_info)
            self._attrs = {"friends": friends_info}

        except Exception as e:
            _LOGGER.error("Error fetching friends list: %s", e)
            self._state = None
            self._attrs = {}
