from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

# eng = create_engine('sqlite:///:gamepass:')

Base = declarative_base()


# games_reviews = Table(
#     "games_reviews",
#     Base.metadata,
#     Column("game_id", Integer, ForeignKey("games.game_id")),
#     Column("review_id"), Integer, ForeignKey("reviews.review_id")
# )


class Games(Base):
    # __tablename__ = "games"
    id = Column(Integer, primary_key=True)
    short_title = Column(String)
    developer_name = Column(String)
    publisher_name = Column(String)
    publisher_website = Column(String)
    support_website = Column(String)
    description = Column(String)
    short_description = Column(String)
    last_modified = Column(DateTime)
    user_rating = Column(Float)
    n_user_rating = Column(Integer)
    poster_url = Column(String)
    reviews = relationship("Reviews", backref="reviews", lazy=True)


class Reviews(Base):
    review_id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("game.id"))
    percent_recommended = Column(Float)
    num_reviews = Column(Integer)
    median_score = Column(Integer)
    average_score = Column(Float)
    percentile = Column(Integer)
    first_released = Column(DateTime)
