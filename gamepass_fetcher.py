from typing import List, Dict

import arrow
import numpy as np
import requests
from sqlalchemy import create_engine

eng = create_engine('sqlite:///:gamepass:')

# URLs used for getting gamepass json data
CATALOG_URL = "https://catalog.gamepass.com/sigls/v2?id=29a81209-df6f-41fd-a528-2ae6b91f719c&language=en-us&market=US"
PRODUCT_URL = "https://displaycatalog.mp.microsoft.com/v7.0/products?bigIds="


class GamePass:
    def __init__(self, catalogue_url: str = CATALOG_URL):
        self.catalogue_url = catalogue_url
        self.date = arrow.now()
        self.catalogue = self.update_catalogue()
        self.num_games = len(self.catalogue)

    def update_catalogue(self) -> List[Dict]:
        """
        Updates the entire gamepass catalogue
        :return: List of gamepass games
        """

        # Gets gamepass catalogue as json and returns all games as a list with dict per game. Skip first since metadata
        catalogue = requests.get(self.catalogue_url).json()
        return [item for item in catalogue[1:]]

    def __repr__(self):
        return f"Gamepass currently has {self.num_games} games as of {self.date.humanize()}"

    def average_user_rating(self):
        """
        Calculates average user rating on the xbox store for all gamepass games
        :return float: average user rating as float
        """
        ratings = []

        # Loop over games in catalogue and get user rating from api
        for game in self.catalogue:
            rating = Game(game.get('id')).game_info['user_ratings'][-1]['AverageRating']
            ratings.append(rating)
        return np.around(np.mean(ratings), 2)


class Game:
    def __init__(self, game_id: str):
        self.id = game_id
        self._game_info = self.parse_game_info()

    # @property
    # def game_info(self):
    #     return self._game_info

    def get_game_info(self):
        info_url = f"https://displaycatalog.mp.microsoft.com/v7.0/products?bigIds={self.id}" \
                   f"&market=US&languages=en-us&MS-CV=DGU1mcuYo0WMM"

        info = requests.get(info_url)
        return info.json()

    def __repr__(self):
        return (f"{self._game_info['name']} released {self._game_info['release_date'].date()}. "
                f"Developed by \"{self._game_info['developer']}\" "
                f"the game has a an average user rating of {self._game_info['user_ratings'][-1]['AverageRating']}/5 "
                f"with {self._game_info['user_ratings'][-1]['RatingCount']} reviews")

    def parse_game_info(self):
        game_info = self.get_game_info()["Products"][0]

        return {
            "last_modified": game_info["LastModifiedDate"],
            "name": game_info["LocalizedProperties"][0]["ShortTitle"],
            "developer": game_info["LocalizedProperties"][0][
                "DeveloperName"
            ],
            "publisher": game_info["LocalizedProperties"][0][
                "PublisherName"
            ],
            "description": game_info["LocalizedProperties"][0][
                "ShortDescription"
            ],
            "image_urls": game_info["LocalizedProperties"][0][
                "Images"
            ],
            "user_ratings": game_info["MarketProperties"][0][
                "UsageData"
            ],
            # "release_date": arrow.get(game_info["MarketProperties"][0]["OriginalReleaseDate"],
            #                                   "%Y-%m-%dT%H:%M:%S.%f0Z")
            "release_date": arrow.get(game_info["MarketProperties"][0]["OriginalReleaseDate"])
        }

    @property
    def game_info(self):
        return self._game_info


# xpass = GamePass()
# ratings = xpass.average_user_rating()
# print(ratings)
# games = [Game(game_id.get("id")) for game_id in xpass.catalogue[1:10]]
#
# for game in games:
#     print(game)
test = Game("9P5VMG8D4P4B")
print(test)
