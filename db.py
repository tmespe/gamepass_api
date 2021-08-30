from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine


# eng = create_engine('sqlite:///:gamepass:')

# Base = declarative_base()


# games_reviews = Table(
#     "games_reviews",
#     Base.metadata,
#     Column("game_id", Integer, ForeignKey("games.game_id")),
#     Column("review_id"), Integer, ForeignKey("reviews.review_id")
# )


class Game(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    short_title: Optional[str] = None
    developer_name: Optional[str] = None
    publisher_name: Optional[str] = None
    publisher_website: Optional[str] = None
    support_website: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    last_modified: Optional[str] = None
    user_rating: Optional[float] = None
    n_user_rating: Optional[int] = None
    poster_url: Optional[str] = None
    # reviews = relationship("Reviews", backref="reviews", lazy=True)


class Review(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    percent_recommended: Optional[int] = None
    num_reviews: Optional[int] = None
    median_score: Optional[int] = None
    average_score: Optional[float] = None
    percentile: Optional[int] = None
    first_released: Optional[str] = None
    game_id: Optional[int] = Field(default=None, foreign_key="game.id")


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_game(game):
    with Session(engine) as session:
        review = game.pop("opencritic")
        review = Review(**review)


def create_review(review):
    with Session(engine) as session:
        pass


def main():
    create_db_and_tables()


if __name__ == "__main__":
    main()
