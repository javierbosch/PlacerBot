import json
import requests
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler)
import logging

api_token = "586911b19bmshbabc3c966931fbbp1cf4c0jsnf5b48f816de9"
api_url_base = 'https://wft-geo-db.p.rapidapi.com/v1/geo/cities?'

def getPhoto(city, id):
    placeSearch= "https://maps.googleapis.com/maps/api/place/textsearch/json?query=" + city + "&key=AIzaSyBsaJ9NkJ8iLYa22-S6jUGUUrJNC4HS84A"    
    responsePlaceSearch = requests.get(placeSearch)
    responsePlaceSearchMeta = json.loads(responsePlaceSearch.content.decode('utf-8'))
    photoID = responsePlaceSearchMeta["results"][0]["photos"][0]["photo_reference"]
    print(city + " Photo ID: " + photoID)
    photoSearch = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=500&photoreference=" + photoID + "&key=AIzaSyBsaJ9NkJ8iLYa22-S6jUGUUrJNC4HS84A"
    image = requests.get(photoSearch)
    print(image.content)
    filename = id + "img.jpg"
    image1 = open(filename, "wb")
    image1.write(image.content)
    return filename

def inList ()

def getNearbyCities(id, rad):
    validCities =[]
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

        for i in range(len(responseMeta["data"])):
            #getPhoto(responseMeta["data"][i]["name"], userID)
            city = [responseMeta["data"][i]["name"],responseMeta["data"][i]["country"]]
            userOBj = users[id]
            if (city not in userOBj.likedCities and city not in userOBj.dislikedCities):
                validCities.append([responseMeta["data"][i]["name"],responseMeta["data"][i]["country"]])

    print(validCities)
    return validCities

    else:
        print("API request failed" + str(responseMeta))
        return None


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
        self.radius = 150
    
    def __str__(self):
        return "name: " + self.name + " age: " + self.age + " gender: " + self.gender + " location: " + str(self.location) + " interests: " + self.interests 

new_user = None

users = {}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

AGE, GENDER, LOCATION, RADIUS, INTERESTS, CONV, NEW = range(7)


def start(bot, update):
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
        update.message.reply_text('Please send your location, in order for me to provide you with convenient results and a better user experience')
                              #  ' or send /skip.')
        return LOCATION
    else:
        update.message.reply_text('Are you sure? What is your real age?')
        return AGE
    

def location(bot, update):
    user = update.message.from_user
    user_location = update.message.location
    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                user_location.longitude)
    users[update.message.chat_id].location=[user_location.latitude, user_location.longitude]
    update.message.reply_text('Thank you! Please pick your radius. (Between 50-500km)')

    return RADIUS


def skip_location(bot, update):
    reply_keyboard = [["Nature", "Big cities", "Western culture", "Eastern culture"]]
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text('You seem a bit paranoid! Please pick your interests.', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return INTERESTS

def radius(bot, update):
    if (int(update.message.text)>49 and int(update.message.text)<501):
        user = update.message.from_user
        logger.info("Radius of %s: %s", user.first_name, update.message.text)
        users[update.message.chat_id].radius=update.message.text
            
        if(users[update.message.chat_id].newloca==True):
                print(users[update.message.chat_id])
                update.message.reply_text('If you want to use the Placer Bot go ahead and type /search!')
                return ConversationHandler.END
        else:
            reply_keyboard = [["Nature", "Big cities", "Western culture", "Eastern culture"]]
            update.message.reply_text('Thank you! Please pick your interests.', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            return INTERESTS
        
    else:
        update.message.reply_text("I wouldn't use that as a radius, remember it's in kilometers. \nWhy don't you consider a different one?")
        return RADIUS

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
    "/info - to get information about the places you liked. \n"
    "/cancel - to cancel the conversation.")

def info(bot, update):
    userObj = users[update.message.chat_id]
    update.message.reply_text("Info! \n")
    s = ""
    for i in range(len(userObj.likedCities)):
        s += userObj.likedCities[i][0] + ", " + userObj.likedCities[i][1] + "\n"
    update.message.reply_text("Alright, this is the list with the places you already liked: \n" + s, reply_markup=ReplyKeyboardRemove())

def newloca(bot, update):
    update.message.reply_text('Alright, send your new location!')
    users[update.message.chat_id].newloca = True
    users[update.message.chat_id].nearbyCities=[]
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
    userObj = users[update.message.chat_id]
    userObj.nearbyCities = getNearbyCities(update.message.chat_id, rad=userObj.radius)
    print(userObj.nearbyCities)
    reply_keyboard= [["💩", "✈"]]
    update.message.reply_text('How do you like ' + userObj.nearbyCities[userObj.i][0] + ", " + userObj.nearbyCities[userObj.i][1] +  '?',
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return CONV
    


def searchAnswer(bot, update):
    user = update.message.from_user
    userObj = users[update.message.chat_id]

    if (update.message.text == "💩"):
        userObj.dislikedCities.append(userObj.nearbyCities[userObj.i])
    else:
        userObj.likedCities.append(userObj.nearbyCities[userObj.i])

    logger.info("%s, %s, %s", user.first_name, update.message.text, userObj.nearbyCities[userObj.i])
    
    if (len(userObj.nearbyCities)-1==userObj.i):
        logger.info("%s, %s, %s", user.first_name, update.message.text, userObj.nearbyCities[userObj.i])
        userObj.i=0    
        reply_keyboard= [["👍", "👎"]]
        update.message.reply_text("Do you want to see more places?",  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return NEW
    else:
        userObj.i+=1
        reply_keyboard= [["💩", "✈"]]
        update.message.reply_text('How do you like ' + userObj.nearbyCities[userObj.i][0] + ", " + userObj.nearbyCities[userObj.i][1]+ '?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return CONV

def new_callback (bot, update):
    userObj = users[update.message.chat_id]

    if (update.message.text == "👍"):
        update.message.reply_text("Cooooool, just type /newloca and discover new places", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        update.message.reply_text("Alright, this is the list with the places you already liked:", reply_markup=ReplyKeyboardRemove())
        s = ""
        for i in range(len(userObj.likedCities)):
            s += userObj.likedCities[i][0] + ", " + userObj.likedCities[i][1] + "\n"
        update.message.reply_text(s + "\n")
        update.message.reply_text("Type /info to see more information about them")       

        return ConversationHandler.END

    


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

            RADIUS: [MessageHandler(Filters.text, radius)],

            INTERESTS: [RegexHandler('^(Nature|Big cities|Western culture|Eastern culture)$', interests)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    loca_handler = ConversationHandler(
        entry_points=[CommandHandler('newloca', newloca)],

        states={
            LOCATION: [MessageHandler(Filters.location, location),
                       CommandHandler('skip', skip_location)],
            
            RADIUS: [MessageHandler(Filters.text, radius)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    tinder_handler = ConversationHandler(
        entry_points=[CommandHandler('search', search)],

        states={
            CONV: [RegexHandler('^(✈|💩)$', searchAnswer)],
            NEW:  [RegexHandler('^(👍|👎)$', new_callback)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("info", info))
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
