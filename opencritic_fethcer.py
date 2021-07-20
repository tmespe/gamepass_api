import requests

OPENCRITIC_SEARCH_API_URL = "https://api.opencritic.com/api/meta/search?"
OPENCRITIC_GAME_INFO_URL = "https://api.opencritic.com/api/game/"


def search_game(name: str) -> int:
    """
    Searches a game name on opencritic and returns the id if result distance is less than 0.5
    :param name: Name of game to search for
    :return id: Opencritic id of game matching search
    :rtype: Int
    """

    # Gets a json of results that matches game name using opencritic API.
    # Returns a sorted list of json with closest match being first
    result = requests.get(OPENCRITIC_SEARCH_API_URL, params={"criteria": name}).json()
    best_match = result[0]

    # If distance between search and the first match is less than 0.5 (0.5 equals guessing?) return game id
    if best_match["dist"] < 0.5:
        return best_match["id"]


def get_game_info(game_id: int) -> dict:
    """
    Returns game info for a given opencritic game_id
    :param game_id: Opencritic game id to get info for
    :return:
    """
    result = requests.get(OPENCRITIC_GAME_INFO_URL + str(game_id)).json()

    # List of keys from api to keep
    relevant_keys = ["name", "percentRecommended", "numReviews", "medianScore", "averageScore", "percentile",
                     "Platforms", "Genres", "firstReleaseDate"]

    # Loop over keys wanted for API and keep those in relevant_keys
    game_info = {key_to_keep: result[key_to_keep] for key_to_keep in relevant_keys}

    return game_info


