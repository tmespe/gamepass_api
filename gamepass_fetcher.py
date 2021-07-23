from typing import List, Dict
import pandas as pd
import arrow
import numpy as np
import requests
from sqlalchemy import create_engine
from opencritic_fethcer import search_game, get_game_reviews

eng = create_engine('sqlite:///:gamepass:')

# URLs used for getting gamepass json data
CATALOG_URL = "https://catalog.gamepass.com/sigls/v2?id=29a81209-df6f-41fd-a528-2ae6b91f719c&language=en-us&market=US"
PRODUCT_URL = "https://displaycatalog.mp.microsoft.com/v7.0/products?bigIds="


class GamePass:
    def __init__(self, catalogue_url: str = CATALOG_URL):
        self.catalogue_url = catalogue_url
        self.date = arrow.now()
        self.catalogue_ids = self.update_catalogue_ids()
        self.catalogue = self.get_all_games_info()

    def update_catalogue_ids(self) -> List[str]:
        """
        Updates the entire gamepass catalogue
        :return: List of gamepass games
        """

        # Gets gamepass catalogue from API and returns a list of all game IDs. Skip first since unnecessary metadata
        catalogue = requests.get(self.catalogue_url).json()
        return [item["id"] for item in catalogue[1:]]

    def __len__(self):
        return len(self.catalogue_ids)

    def __repr__(self):
        return f"Gamepass currently has {len(self)} games as of {self.date.humanize()}"

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

    def get_all_games_info(self):
        relevant_keys = ["name", "percentRecommended", "numReviews", "medianScore", "averageScore", "percentile",
                         "Platforms", "Genres", "firstReleaseDate"]

        info_url = f"https://displaycatalog.mp.microsoft.com/v7.0/products?bigIds={','.join(self.catalogue_ids)}" \
                   f"&market=US&languages=en-us&MS-CV=DGU1mcuYo0WMM"

        json_data = requests.get(info_url).json()["Products"]
        df = self.to_pandas_df(json_data)
        df.set_index("ProductTitle", inplace=True)
        return df.to_dict(orient="index")

    def get_opencritic_reviews(self):
        pass

    @staticmethod
    def to_pandas_df(data):
        """
        Cleans and converts gamepass catalogue to pandas dataframe
        :return pd.Dataframe: A pandas dataframe
        """
        # Set unwanted fields to be removed form dataframe
        columns_to_drop = ["Franchises", "FriendlyTitle", "SearchTitles", "VoiceTitle", "RenderGroupDetails",
                           "ProductDisplayRanks", "Interactive3DEnabled", "Language", "InteractiveModelConfig",
                           "EligibilityProperties.Affirmations", "EligibilityProperties.Remediations", "Markets",
                           "Videos"]

        # Use json_normalize to flatten json
        df = pd.json_normalize(data, "LocalizedProperties", ["LastModifiedDate", "MarketProperties"])
        df = df.drop(columns=columns_to_drop)
        # Replace empty strings with NaN to since necessary to use fillna
        df = df.replace(r'^\s*$', np.nan, regex=True)

        # Fill "ShorTitle" with values from "SortTitle" where missing and "SortTitle" has values.
        df["ShortTitle"] = df["ShortTitle"].fillna(df["SortTitle"])
        # Get average rating and n_ratings all time from MarketProperties which also contains 7 and 30 days
        df["user_rating"] = df["MarketProperties"].apply(lambda x: x["UsageData"][-1]["AverageRating"]).astype("int")
        df["n_user_rating"] = df["MarketProperties"].apply(lambda x: x["UsageData"][-1]["RatingCount"]).round()
        # Get URL for poster from Images for use in visualization.
        df["poster_url"] = df["Images"].apply(lambda x: x[4]["Uri"])
        # Drop columns that have been processed and are no longer needed
        df = df.drop(columns=["Images", "MarketProperties", "SortTitle"], axis=1)
        # Move "ShorTitle" first in dataframe and drop duplicate middle column
        df.insert(0, "ShortTitle", df['ShortTitle'], allow_duplicates=True)
        df = df.drop(df.columns[7], axis=1)

        return df


class Game:
    def __init__(self, game_id: str):
        self.id = game_id
        self._game_info = self.parse_game_info()

    # @property
    # def game_info(self):
    #     return self._game_info

    def get_game_info(self):
        info_url = f"{PRODUCT_URL}{self.id}" \
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
            "release_date": arrow.get(game_info["MarketProperties"][0]["OriginalReleaseDate"])
        }

    @property
    def game_info(self):
        return self._game_info


xpass = GamePass()
# df = xpass.to_pandas_df()
print(xpass)
# games = [Game(game_id.get("id")) for game_id in xpass.catalogue[1:10]]
#
# for game in games:
#     print(game)
# test = Game("9P5VMG8D4P4B")
# print(test)
