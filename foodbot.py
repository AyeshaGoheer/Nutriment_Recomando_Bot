import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from sqlalchemy.orm import sessionmaker

from constants import API_ENDPOINT, API_KEY, TELEGRAM_API_KEY
from utils import Conversation, State, map_price_range
from database import History, engine

Session = sessionmaker(bind=engine)
session = Session()
conversations = {}


def start(update, callback):
    username = update.message.from_user.username

    # Greet the user and introduce the bot
    greeting = f'Hello {username}! I am Nutriment Recomando bot. I can help you find great ' \
               'restaurants based on your location, cuisine preferences, and price range. ' \
               'Send /recommend command to get started.\nStill confused? send /help command for more info'
    callback.bot.send_message(chat_id=update.effective_chat.id, text=greeting)


def recommend(update, callback):
    chat_id = update.message.chat_id

    # Check if the chat id is in the dictionary
    if chat_id not in conversations:
        # Create a new Conversation object and add it to the dictionary
        conversations[chat_id] = Conversation()
        # Get the Conversation object for the chat id
        conversation = conversations[chat_id]
        conversation.state = State.LOCATION

    # Ask the user for their location
    location_request = 'Please tell me your location so I can recommend restaurants nearby.'

    callback.bot.send_message(chat_id=update.effective_chat.id, text=location_request)


def helper(update, callback):
    message = "To use this bot, send me a message with the location, cuisine, and price range you are interested in. " \
              "For example, you can send me a message like this:\n\n" \
              "Please enter a location: San Francisco\n" \
              "What cuisine are you looking for?: Italian\n" \
              "Please specify a price range: moderate\n\n" \
              "You can also check your history by sending me the /history command." \
              "Send /recommend to get started or /help to see this message again."

    # Send a message to the user with the help text
    callback.bot.send_message(chat_id=update.effective_chat.id, text=message)


# Define the command handler for the /history command
def history(update, callback):
    # Get the user's ID
    user_id = update.effective_user.id

    # Query the history table for the user's requests and responses
    user_history = session.query(History).filter(History.user_id == user_id).all()

    if user_history:
        # Build the message to send to the user
        message = 'Here is your history:\n\n'
        for h in user_history:
            message += f'Request: {h.request}\n'
            message += f'Response: {h.response}\n'
            message += f'Timestamp: {h.timestamp}\n'
            message += '\n'
    else:
        message = 'You have no history yet.'

    # Send the message to the user
    callback.bot.send_message(chat_id=update.effective_chat.id, text=message)


# A function to handle incoming messages
def handle_message(update, callback):
    # Get the message text and chat id
    message_text = update.message.text
    chat_id = update.message.chat_id

    # Get the Conversation object for the chat id
    conversation = conversations[chat_id]

    # Check the current state of the conversation
    if conversation.state == State.LOCATION:
        # Extract the location from the message text
        location = message_text

        # Check if the location is not empty
        if location:
            # Update the location in the Conversation object
            conversation.location = location
            conversation.state = State.CUISINE

            # Send a message to the user asking for a cuisine
            callback.bot.send_message(chat_id=chat_id, text='What cuisine are you looking for?')
        else:
            # Send a message to the user asking for a location
            callback.bot.send_message(chat_id=chat_id, text='Please enter a location.')
    elif conversation.state == State.CUISINE:
        # Extract the cuisine from the message text
        cuisine = message_text

        # Check if cuisine
        if cuisine:
            # Update the cuisine in the conversation object
            conversation.cuisine = cuisine
            conversation.state = State.PRICE_RANGE

            # Send a message to user asking for price range
            callback.bot.send_message(chat_id=chat_id,
                                      text="Please specify a price range like affordable, luxurious, etc.")
        else:
            callback.bot.send_message(chat_id=chat_id, text="What cuisine are you looking for?")
    elif conversation.state == State.PRICE_RANGE:
        # Extract the price range
        price = map_price_range(message_text)

        # Check if price
        if price:
            # Update the price in the conversation object
            conversation.price_range = price
            conversation.state = State.UNSET

            callback.bot.send_message(chat_id=chat_id,
                                      text="Please wait! I'll find some great recommendations for you shortly")

            # Set up the API parameters
            params = {
                'location': conversation.location,
                'term': conversation.cuisine,
                'price': conversation.price_range,  # 1 and 2 represent "Inexpensive" and "Moderate" price ranges
                'limit': 5,  # Maximum number of results to return
            }

            # Send a GET request to the API endpoint
            response = requests.get(API_ENDPOINT, params=params, headers={'Authorization': f'Bearer {API_KEY}'})
            # Check the response status code
            if response.status_code == 200:
                # Parse the response data
                data = response.json()
                businesses = data['businesses']

                # Build the message to send to the user
                message = 'Here are some recommendations for you:\n\n'
                for b in businesses:
                    message += f'* {b["name"]} ({b["price"]})\n'
                    message += f'  Location: {b["location"]["city"]}\n'
                    message += f'  Rating: {b["rating"]}\n'
                    message += f'  Review count: {b["review_count"]}\n'
                    message += '\n'

                # Send the message to the user
                callback.bot.send_message(chat_id=chat_id, text=message)
                # Store data in the database
                request_string = f'{conversation.cuisine} food in {conversation.location} '
                user_history = History(user_id=chat_id, request=request_string, response=message)
                session.add(user_history)
                session.commit()
                # Clear the conversation
                conversations[chat_id] = Conversation()
                callback.bot.send_message(
                    chat_id=chat_id,
                    text="Enjoy your meal!\n If you need some more recommendations "
                         "the click /recommend for more recommendations, "
                         "/history to view your history or /help for more info."
                )
            else:
                # The request failed, send an error message to the user
                callback.bot.send_message(
                    chat_id=chat_id,
                    text='Sorry, I was unable to find any recommendations for you. '
                         'Send /help or /recommend to try again.'
                )
                # Clear the conversation
                conversations[chat_id] = Conversation()
        else:
            callback.bot.send_message(chat_id=chat_id,
                                      text="Please specify a price range like affordable, luxurious, etc.")


# Create an Updater object and attach a dispatcher to it
updater = Updater(token=TELEGRAM_API_KEY)
dispatcher = updater.dispatcher

# Add a handler for the MessageHandler and CommandHandler
start_handler = CommandHandler('start', start)
recommend_handler = CommandHandler('recommend', recommend)
help_handler = CommandHandler('help', helper)
history_handler = CommandHandler('history', history)
message_handler = MessageHandler(Filters.text, handle_message)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(recommend_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(history_handler)
dispatcher.add_handler(message_handler)

# Start the bot
updater.start_polling()

# Run the bot until you press Ctrl-C
updater.idle()
