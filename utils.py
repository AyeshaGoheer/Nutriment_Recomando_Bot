from enum import Enum


class State(Enum):
    LOCATION = 1
    CUISINE = 2
    PRICE_RANGE = 3
    UNSET = 4


class Conversation:
    def __init__(self):
        self.state = State.LOCATION
        self.location = ''
        self.cuisine = ''
        self.price_range = ''


def map_price_range(price_range):
    # Map the price range terms to numerical values for the Yelp API
    if price_range.lower() in ['inexpensive', 'cheap']:
        return 1
    elif price_range.lower() in ['moderate', 'affordable']:
        return 2
    elif price_range.lower() in ['pricey', 'expensive']:
        return 3
    elif price_range.lower() in ['ultra high-end', 'luxurious']:
        return 4
    else:
        # Return 2 as a default value
        return 2

