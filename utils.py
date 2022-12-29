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





# # Set up the API endpoint and API key
# API_ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
# API_KEY = 'IbFwE8nxLP5y2_8Vveyi1vN7UFCaEHtTPwIQrjnmbdBrbjrgerIprLguWfY8TeapNXksyPAPcGeAf_zp3-fN7G9yEtGkF4aaB61b48q3dtBXl_jMQjzWELpjelGpY3Yx'
#
# # Set up the API parameters
# params = {
#     'location': 'New York',
#     'term': 'food',
#     'price': '1,2',  # 1 and 2 represent "Inexpensive" and "Moderate" price ranges
#     'limit': 5,  # Maximum number of results to return
# }
#
# # Send a GET request to the API endpoint
# response = requests.get(API_ENDPOINT, params=params, headers={'Authorization': f'Bearer {API_KEY}'})
#
# # Check the response status code
# if response.status_code == 200:
#     # Parse the response data
#     data = response.json()
#     businesses = data['businesses']
#
#     # Iterate over the businesses and print their names and locations
#     for b in businesses:
#         print(f'{b["name"]} ({b["location"]["city"]})')
# else:
#     # Print an error message if the request fails
#     print(f'Error: {response.status_code}')
