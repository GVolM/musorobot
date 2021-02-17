# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 20:34:30 2021

@author: AVALON
"""

from telegram import ReplyKeyboardMarkup, KeyboardButton, ForceReply, Update
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater, ConversationHandler, CallbackContext
import json

TOKEN = '****************************'

location_keyboard = KeyboardButton(text="send_location",  request_location=True)           #creating location button object
contact_keyboard = KeyboardButton('Share contact', request_contact=True)  #creating contact button object
custom_keyboard = [[ location_keyboard, contact_keyboard ]] #creating keyboard object
reply_markup = ReplyKeyboardMarkup(custom_keyboard)  

CHOOSING, COORDINATES, TYPE_JUNK, PHOTO, COMMENT= range(5)
def run(updater):
    updater.start_polling()
    updater.idle()   
    
def main():
    mybot = Updater(TOKEN)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", start))
    #dp.add_handler(MessageHandler(Filters.text, reply))
    #dp.add_handler(MessageHandler(Filters.location, location_got))
    #dp.add_handler(MessageHandler(Filters.reply, reply))
    converstion_handler=ConversationHandler(
        entry_points=[CommandHandler('new', new_spot)], 
        states={CHOOSING:[MessageHandler(Filters.regex('^Координаты$'), coordinates_chosen),
                          MessageHandler(Filters.regex('^вид мусора$'), type_chosen),
                          MessageHandler(Filters.regex('^фото$'), photo_chosen),
                          MessageHandler(Filters.regex('^комментарий$'), comment_chosen),
                          MessageHandler(Filters.regex('^готово$'), complete)],
                COORDINATES:[MessageHandler(Filters.location, add_location)],
                TYPE_JUNK:[MessageHandler(Filters.regex('^(пластик|биомусор|строительный|смешанный)$'), add_junk_type)],
                PHOTO:[MessageHandler(Filters.photo, add_photo)],
                COMMENT:[MessageHandler(Filters.text & Filters.reply, add_comment)],
                },
                fallbacks=[MessageHandler(Filters.regex('^Спасибо!$'), done)],
                name='get data conv',
                allow_reentry=True)
    dp.add_handler(converstion_handler)
    run(mybot)
reply_keyboard_main=[['Координаты','вид мусора'],['фото','комментарий'],['готово'] ]
reply_keyboard_type=[['пластик','биомусор'],['строительный','смешанный']]

markup_main=ReplyKeyboardMarkup(reply_keyboard_main, one_time_keyboard=True)

markup_type=ReplyKeyboardMarkup(reply_keyboard_type, one_time_keyboard=True)

def new_spot(update: Update, context: CallbackContext) -> None:
    reply_text='Привет, видимо ты обнаружил мусор, ответь на все вопросы и мы отметим его на нашей карте'
    update.message.reply_text(reply_text,reply_markup=markup_main)
    #del context.user_data
    context.user_data['comment']=None
    context.user_data['location']=None
    context.user_data['photo']=None
    context.user_data['type']=None
    
    return CHOOSING


def coordinates_chosen(update: Update, context: CallbackContext) -> None:
    reply_text='хорошо начнем с координат, поделитесь со мной координатами'
    update.message.reply_text(reply_text)
    return COORDINATES

def type_chosen(update: Update, context: CallbackContext) -> None:
    reply_text='теперь выбирите тип'
    update.message.reply_text(reply_text, reply_markup=markup_type)
    return TYPE_JUNK

def photo_chosen(update: Update, context: CallbackContext) -> None:
    reply_text='может и фотография есть?'
    update.message.reply_text(reply_text)
    return PHOTO

def comment_chosen(update: Update, context: CallbackContext) -> None:
    reply_text='напишите дополнительную информацию'
    update.message.reply_text(reply_text, reply_markup=ForceReply())
    return COMMENT

def add_location(update: Update, context: CallbackContext) -> None:
    location=update.message.location
    context.user_data['location']=location
    reply_text='Атлична, ААтлична! Что еще ты мне сможешь рассказать?'
    update.message.reply_text(reply_text, reply_markup=markup_main)
    return CHOOSING

def add_junk_type(update: Update, context: CallbackContext) -> None:
    text=update.message.text
    context.user_data['type']=text
    reply_text='Великолепно! Что еще ты мне сможешь рассказать?'
    update.message.reply_text(reply_text, reply_markup=markup_main)
    return CHOOSING

def add_photo(update: Update, context: CallbackContext) -> None:
    photo_id=update.message.photo[0].file_id
    context.user_data['photo']=photo_id
    reply_text='отличная фотка! Что еще ты мне сможешь рассказать?'
    update.message.reply_text(reply_text, reply_markup=markup_main)
    return CHOOSING
    

def add_comment(update: Update, context: CallbackContext) -> None:
    comment=update.message.text
    context.user_data['comment']=comment
    reply_text='Спасибо за комментарий! Что еще ты мне сможешь рассказать?'
    update.message.reply_text(reply_text, reply_markup=markup_main)
    return CHOOSING

def complete(update: Update, context: CallbackContext) -> None:
    if (context.user_data['comment'])and(context.user_data['location'])and(context.user_data['photo'])and(context.user_data['type']):
        reply_text='Спасибо, ваша заявка принята и вскоре она будет отмечена на нашей карте'
        update.message.reply_text(reply_text,reply_markup=ReplyKeyboardMarkup([['Спасибо!']], one_time_keyboard=True))
        user_id=update.message.from_user.id
        date=update.message.date
        data={'date':str(date),
              'user_id':user_id,
              'longitude':context.user_data['location'].longitude,
              'latitude':context.user_data['location'].latitude,
              'photo':context.user_data['photo'],
              'type':context.user_data['type'],
              'comment':context.user_data['comment']
              }
        with open('data.json', 'a') as fp:
            json.dump(data, fp,indent=2)
    else:
        reply_text='ты что-то от меня скрываешь, попробуй еще раз'
        update.message.reply_text(reply_text, reply_markup=markup_main)
        return CHOOSING
    
    
def start(update: Update, context: CallbackContext):
    reply_text="Привет, я мусоробот. Я собираю инвормацию о мусоре на просторах нашей страны. Если вы видете мусор пришлите мне геометку, а потом я спрошу вас про колличество мусора. Данные будут обработанны и отображены на карте по ссылке... "
    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup([['/new']], one_time_keyboard=True)) 
                
    
def done(update: Update, context: CallbackContext):
    reply_text='Вам спсибо!'
    update.message.reply_text(reply_text,reply_markup=ReplyKeyboardMarkup([['/new']], one_time_keyboard=True))
    
if __name__=='__main__':
    main()
