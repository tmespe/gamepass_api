from typing import List, Dict

import arrow
import numpy as np
import pandas as pd
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
        # self.catalogue_ids = self.update_catalogue_ids()
        self.catalogue = self.get_all_games_info()

    @property
    def catalogue_ids(self) -> List[str]:
        """
        Gets ids for all games in the catalogue
        :return List: List of ids for all gamepass games
        """

        # Skip first entry since unnecessary metadata
        catalogue = requests.get(self.catalogue_url).json()

        return [item["id"] for item in catalogue[1:]]

    def __len__(self):
        return len(self.catalogue_ids)

    def __repr__(self):
        return f"Gamepass currently has {len(self)} games as of {self.date.humanize()}"

    @property
    def average_user_rating(self):
        """
        Calculates average user rating on the xbox store for all gamepass games
        :return float: average user rating as float
        """
        ratings = [game["user_rating"] for game in self.catalogue.values()]

        return np.around(np.mean(ratings), 2)

    def get_all_games_info(self) -> Dict:
        """
        Gets all game information for all games in the gamepass catalogue
        :return Dict: Dict of strings with game name as key and DeveloperName, PublisherName, PublisherUrl, SupportUrl,
        Description, ShortDescription, LastModifiedDate, UserRating, N_UserRating, PosterUrl
        """

        info_url = f"https://displaycatalog.mp.microsoft.com/v7.0/products?bigIds={','.join(self.catalogue_ids)}" \
                   f"&market=US&languages=en-us&MS-CV=DGU1mcuYo0WMM"

        json_data = requests.get(info_url).json()["Products"]
        # Use to_pandas method to flatten json and clean data
        df = self.to_pandas_df(json_data)
        # Set game title as index and use pandas to dict to return a dict with name as key and info as values
        df.set_index("ProductTitle", inplace=True)
        return df.to_dict(orient="index")

    def get_opencritic_reviews(self):
        """
        Gets review data for all games in the gampeass catalogue
        :return Dict: Dict with game name as key and review scores as value
        """
        for game, info in self.catalogue.items():
            short_title = info["short_title"]
            opencritic_id = search_game(game)

            if type(opencritic_id) == int:
                reviews = get_game_reviews(opencritic_id)
                self.catalogue[game]["opencritic"] = reviews
            else:
                self.catalogue[game]["opencritic"] = None

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
        df.insert(0, "short_title", df['ShortTitle'])
        df = df.drop("ShortTitle", axis=1)

        return df


if __name__ == '__main__':
    xpass = GamePass()
    xpass.get_opencritic_reviews()
# df = xpass.to_pandas_df()
