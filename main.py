import json
import requests
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler)
import logging

api_token = "586911b19bmshbabc3c966931fbbp1cf4c0jsnf5b48f816de9"
api_url_base = 'https://wft-geo-db.p.rapidapi.com/v1/geo/cities?'

radius = 300
validCities = {}

def getNearbyCities(id, rad = radius):
    headers = {'X-RapidAPI-Key' : api_token}
    sign1 = "%2B" if users[id].location[0] > 0 else ""
    sign2 = "%2B" if users[id].location[1] > 0 else ""

    print(users[id].location)
    requestString = api_url_base + 'location=' + sign1 + str(users[id].location[0]) + sign2 + str(users[id].location[1]) + '&radius=' + str(rad) + '&distanceUnit=KM&sort=-population'
    print(requestString)
    response = requests.get(requestString, headers = headers)
    responseMeta = json.loads(response.content.decode('utf-8'))

    if(response.status_code == 200):

        print("sucessfull: "  + str(responseMeta["data"]))

        for i in range(len(responseMeta)):
            validCities[0][i] = responseMeta["data"][i]["name"]
            validCities[1][i] = responseMeta["data"][i]["country"]

        print(validCities)
        return validCities

    else:
        print("API request failed" + str(responseMeta))
        return None

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

class User:
    def __init__(self):
        self.name = None
        self.age = None
        self.gender = None
        self.location = None
        self.interests = None
        self.nearbyCities = []
        self.likedCities = []
        self.dislikedCities = []
        self.newloca = False
        self.i = 0
    
    def __str__(self):
        return "name: " + self.name + " age: " + self.age + " gender: " + self.gender + " location: " + str(self.location) + " interests: " + self.interests 

new_user = None

users = {}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

AGE, GENDER, LOCATION, INTERESTS, CONV = range(5)


def start(bot, update):
    new_user = update.message.chat_id
    users[update.message.chat_id]=User()
    reply_keyboard = [['Male', 'Female', 'Other']]
    user = update.message.from_user
    update.message.reply_text(
        "Hi, " + user.first_name + "! Welcome to Placer. Please answer the following questions. \n\n"
        'Are you male or female?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    users[update.message.chat_id].name=user.first_name

    return GENDER


def gender(bot, update):
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    users[update.message.chat_id].gender=update.message.text

    update.message.reply_text('What is your age?',
        reply_markup=ReplyKeyboardRemove())

    return AGE


def age(bot, update):
    if (int(update.message.text)>0 and int(update.message.text)<120):
        user = update.message.from_user
        logger.info("Age of %s: %s", user.first_name, update.message.text)
        users[update.message.chat_id].age=update.message.text
        update.message.reply_text('Please send us your location, in order for us to provide you with convenient results and a better user experience'
                                ' or send /skip.')
        return LOCATION
    else:
        update.message.reply_text('Are you sure? What is your real age?')
        return AGE
    

def location(bot, update):
    reply_keyboard = [["Nature", "Big cities", "Western culture", "Eastern culture"]]
    user = update.message.from_user
    user_location = update.message.location
    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                user_location.longitude)
    users[update.message.chat_id].location=[user_location.latitude, user_location.longitude]

    if(users[update.message.chat_id].newloca==True):
        print(users[update.message.chat_id])
        update.message.reply_text('If you want to use the Placer Bot go ahead and type /search!')
        return ConversationHandler.END
    else:
        update.message.reply_text('Thank you! Please pick your interests.', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return INTERESTS


def skip_location(bot, update):
    reply_keyboard = [["Nature", "Big cities", "Western culture", "Eastern culture"]]
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text('You seem a bit paranoid! Please pick your interests.', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return INTERESTS


def interests(bot, update):

    user = update.message.from_user
    logger.info("Interest of %s: %s", user.first_name, update.message.text)
    users[update.message.chat_id].interests=update.message.text
    update.message.reply_text('If you want to use the Placer Bot go ahead and type /search!',reply_markup=ReplyKeyboardRemove())

    print(users[update.message.chat_id])
    return ConversationHandler.END

def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text("This is the list of commands: \n\n"
    "/start - to start a conversation with the bot. All your data will be deleted. \n"
    "/newloca - to identify your new location. \n"
    "/search - to use the Placer Bot and to identify cities near you. \n"
    "/cancel - to cancel the conversation.")


def newloca(bot, update):
    update.message.reply_text('Alright, send us your new location!')
    users[update.message.chat_id].newloca = True
    return LOCATION


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def search(bot, update):
    user = update.message.from_user
    userObj = users[update.message.chat_id]
    userObj.nearbyCities = []
    userObj.nearbyCities = getNearbyCities(update.message.chat_id, rad=radius)
    print(userObj.nearbyCities)
    reply_keyboard= [["💩", "✈"]]
    update.message.reply_text('How do you like ' + userObj.nearbyCities[0][userObj.i] + '?',
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    if (len(userObj.nearbyCities[0])==userObj.i):
        userObj.i=0  
        return ConversationHandler.END
    else:
        return CONV


def searchAnswer(bot, update):
    user = update.message.from_user
    userObj = users[update.message.chat_id]
    if (update.message.text == "💩"):
        userObj.dislikedCities.append(userObj.nearbyCities[userObj.i])
    else:
        userObj.likedCities.append(userObj.nearbyCities[userObj.i])
    logger.info("%s, %s, %s", user.first_name, update.message.text, userObj.nearbyCities[userObj.i])
    userObj.i+=1


    


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("822290702:AAEaI2pAKcer5Def1xqBn0ISJ_6CmAnzFrI")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            GENDER: [RegexHandler('^(Male|Female|Other)$', gender)],

            AGE: [MessageHandler(Filters.text, age)],

            LOCATION: [MessageHandler(Filters.location, location),
                       CommandHandler('skip', skip_location)],
            INTERESTS: [RegexHandler('^(Nature|Big cities|Western culture|Eastern culture)$', interests)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    loca_handler = ConversationHandler(
        entry_points=[CommandHandler('newloca', newloca)],

        states={
            LOCATION: [MessageHandler(Filters.location, location),
                       CommandHandler('skip', skip_location)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    tinder_handler = ConversationHandler(
        entry_points=[CommandHandler('search', search)],

        states={
            CONV: [RegexHandler('^(✈|💩)$', searchAnswer)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(conv_handler)
    dp.add_handler(loca_handler)
    dp.add_handler(tinder_handler)
    

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
