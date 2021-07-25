from typing import Union, Any

import requests

OPENCRITIC_SEARCH_API_URL = "https://api.opencritic.com/api/meta/search?"
OPENCRITIC_GAME_INFO_URL = "https://api.opencritic.com/api/game/"


def search_game(name: str) -> Union[dict[str, int], int, str]:
    """
    Searches a game name on opencritic and returns the id if result distance is less than 0.5
    :param name: Name of game to search for
    :return id: Opencritic id of game matching search
    :rtype: Int
    """

    # Gets a json of results that matches game name using opencritic API.
    # Returns a sorted list of json with closest match being first
    try:
        result = requests.get(OPENCRITIC_SEARCH_API_URL, params={"criteria": name}).json()
        best_match = result[0]

        # If distance between search and the first match is less than 0.5 (0.5 equals guessing?) return game id
        if best_match["dist"] < 0.5:
            return best_match["id"]
        else:
            return {"name": name, "id": best_match["id"], "dist": best_match["dist"]}
    except requests.exceptions.RequestException as e:
        return f"Failed to get game id. Is there an issue with gamepass API? Got the following error: {e}"


def get_game_reviews(game_id: int) -> Union[dict, None, str]:
    """
    Returns game info for a given opencritic game_id
    :param game_id: Opencritic game id to get info for
    :return:
    """
    # List of keys from api to keep
    relevant_keys = ["name", "percentRecommended", "numReviews", "medianScore", "averageScore", "percentile",
                     "Platforms", "Genres", "firstReleaseDate"]

    try:
        result = requests.get(OPENCRITIC_GAME_INFO_URL + str(game_id)).json()
        return {key_to_keep: result[key_to_keep] for key_to_keep in relevant_keys}
    except KeyError:
        return None
    except requests.exceptions.RequestException as e:
        return f"Failed to get game id. Is there an issue with gamepass API? Got the following error: {e}"


if __name__ == '__main__':
    info = get_game_reviews(search_game("fallout 76"))
    print(info)
