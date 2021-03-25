# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 20:34:30 2021

@author: AVALON
"""
import datetime
import time
import logging
#from typing import Tuple, Dict, Any
from telegram import (#ReplyKeyboardMarkup, 
                      #KeyboardButton, 
                      #ForceReply, 
                      Update, 
                      InlineKeyboardMarkup, 
                      InlineKeyboardButton,
                      )
from telegram.ext import (CommandHandler, 
                          Filters, 
                          MessageHandler, 
                          Updater, 
                          ConversationHandler, 
                          CallbackContext,
                          CallbackQueryHandler)
import requests
from settings import URL, TOKEN



logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

#%% difinitions
#top level
SELECTING_START, CHOOSING ,SHOW_MAP, ADD_SPOT, ADDING_SPOT, SHOW_SPOTS, DONATE=map(chr, range(7))
#add_spot
ADD_LOCATION, ADD_PHOTO, CHOOSE_TYPE, ADD_COMMENT, SAVE_TICKET, SHOW_TICKET, DIRECT_DONATE, STOPPING=map(chr, range(7,15))

COORDINATES, TYPE_JUNK, PHOTO, COMMENT= map(chr,range(15,19))
#junk type
PLASTIC, GLASS, METAL, ORGANIC = map(chr,range(19,23))
#size_D
SMALL_D, MEDIUM_D, LARGE_D=map(chr,range(23,26))

#amount
#BAG, CAR, TRUCK = map(chr,range(22,25))

END = ConversationHandler.END

TYPES = {        
        'PLASTIC': 0 ,
         'ORGANIC':1,
        'METAL': 2,
        'GLASS':3,
        }
server_url=URL
#%%% inline keyboards
#%%strat keyboard
start_buttons=[[InlineKeyboardButton(text='Map', url= URL,callback_data=str(SHOW_MAP))],
               [InlineKeyboardButton(text='Add spot', callback_data=str(ADD_SPOT)),
                InlineKeyboardButton(text='Show my spots', callback_data=str(SHOW_SPOTS))],
               [InlineKeyboardButton(text='Random donat', callback_data=str(DONATE))]
              ]

start_keyboard=InlineKeyboardMarkup(start_buttons)
#%%add spot keyboard
add_spot_buttons=[[InlineKeyboardButton(text='location', callback_data=str(ADD_LOCATION)),InlineKeyboardButton(text='photo', callback_data=str(ADD_PHOTO))],
                  [InlineKeyboardButton(text='type', callback_data=str(CHOOSE_TYPE)),InlineKeyboardButton(text='comment', callback_data=str(ADD_COMMENT))],
                  [InlineKeyboardButton(text='save', callback_data=str(SAVE_TICKET)),InlineKeyboardButton(text='show', callback_data=str(SHOW_TICKET))],
                  [InlineKeyboardButton(text='direct donate', callback_data=str(DIRECT_DONATE))]
                  ]

add_spot_keyboard=InlineKeyboardMarkup(add_spot_buttons)
#%%choose type keyboard
choose_type_buttons = [[InlineKeyboardButton(text='plastic', callback_data='PLASTIC'),InlineKeyboardButton(text='glass', callback_data='GLASS')],
                       [InlineKeyboardButton(text='metal', callback_data='METAL'),InlineKeyboardButton(text='organic', callback_data='ORGANIC')]
                       ]
choose_type_keyboard = InlineKeyboardMarkup(choose_type_buttons)
#%%choose amount keyboard
#choose_amount_buttons = [[InlineKeyboardButton(text='bag', callback_data=str(BAG))],
#                      [InlineKeyboardButton(text='car', callback_data=str(CAR))],
#                       [InlineKeyboardButton(text='truck', callback_data=str(TRUCK))]
#                       ]

#choose_amount_keyboard = InlineKeyboardMarkup(choose_amount_buttons)
#%%
choose_size_d_buttons = [[InlineKeyboardButton(text='1\%', callback_data=str(SMALL_D))],
                       [InlineKeyboardButton(text='3\%', callback_data=str(MEDIUM_D)),InlineKeyboardButton(text='5\%', callback_data=str(LARGE_D))],   
                       ]
#TODO spiral numbers pattern

choose_size_d_keyboard = InlineKeyboardMarkup(choose_size_d_buttons)
#%%%dynemic keyboard

#def dynamic_keyboard(context, buttons):
#    for lines in buttons:
#        for button in lines:
 #           if context[str(button.text)] != None:
#                print(button.text)
                #button.text=button.text + ' v'
 #   return InlineKeyboardMarkup(buttons)

#%%



def add_spot(update: Update, context: CallbackContext) -> str:
    reply_text='''You probably see some trash, just share with me what you see and I will send it around. \n
Choose categories in the menu below and follow further instructions. To check what you have already sent press "show"            
    
    '''
    #del context.user_data
    context.user_data['comment']=None
    context.user_data['location']=None
    context.user_data['photo']=None
    context.user_data['type']=None
    context.user_data['donat']=None
    context.user_data['random_donat']=0
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=reply_text, reply_markup=add_spot_keyboard)
    return CHOOSING


def coordinates_chosen(update: Update, context: CallbackContext) -> None:
    reply_text='''Ok, let\'s start with coordinates. Send me geotag. To do so, go to upload menu\n
                             \\\\\n
                                \\\\\n
                                   \\\\\n
                                       >>>>
        '''
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=reply_text, reply_markup=None)
    return COORDINATES

def type_chosen(update: Update, context: CallbackContext) -> None:
    reply_text='Can you identify the type of the trash?'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=reply_text, reply_markup=choose_type_keyboard)
    return TYPE_JUNK

def photo_chosen(update: Update, context: CallbackContext) -> None:
    reply_text='Any photo will be so useful for me, send me one please :)'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=reply_text, reply_markup=None)
    return PHOTO

def comment_chosen(update: Update, context: CallbackContext) -> None:
    reply_text='What can you tell me more? Text me please'
    update.callback_query.answer()
    update.callback_query.edit_message_text(reply_text, reply_markup=None)
    return COMMENT

def donate_chosen(update: Update, context: CallbackContext) -> None:
    reply_text=''''Great, you can donate me some money and i will give it to someone who will clean it\n
    \n
How much can you give?'''
    update.callback_query.answer()
    update.callback_query.edit_message_text(reply_text, reply_markup=choose_size_d_keyboard)
    return DONATE

def add_location(update: Update, context: CallbackContext) -> None:
    location=update.message.location
    context.user_data['location']=location
    reply_text='''Super! Now I can calculate an optimal route to clean it with maximum efficiency.\n
    \n
What else can you tell me?
    '''
    update.message.reply_text(reply_text, reply_markup=add_spot_keyboard)
    return CHOOSING

def add_junk_type(update: Update, context: CallbackContext) -> str:
    
    
    context.user_data['type']=update.callback_query.data
    reply_text='''Oo, it will help me a lot to recycle it!\n
    \n
Check what is missing using \'show\' button
    '''
    
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=reply_text, reply_markup=add_spot_keyboard)
    return CHOOSING

def add_photo(update: Update, context: CallbackContext) -> None:
    photo_id=update.message.photo[0].file_id
    context.user_data['photo']=photo_id
    reply_text='''Nice photo! It will help me to find it here\n
    \n
Anything else?'''
    update.message.reply_text(reply_text, reply_markup=add_spot_keyboard)
    return CHOOSING
    

def add_comment(update: Update, context: CallbackContext) -> None:
    comment=update.message.text
    context.user_data['comment']=comment
    reply_text='''Your comment is really useful.\n 
    \n
That\'s all?'''
    
    update.message.reply_text(reply_text, reply_markup=add_spot_keyboard) 
    
    return CHOOSING

def complete(update: Update, context: CallbackContext) -> None:
    if (context.user_data['comment'])and(context.user_data['location'])and(context.user_data['photo'])and(context.user_data['type']):
        reply_text='''Cool, I will show it to everyone and, may be, there will be someone who will be able to clean up here %)\n
        \n
Hope to see you soon with more information
        '''
        #update.message.reply_text(reply_text,reply_markup=ReplyKeyboardMarkup([[InlineKeyboardButton(text='Thanks', callback_data=str(END))]], one_time_keyboard=True))
        user_id=update.callback_query.from_user.id
        date=str(datetime.datetime.now())
        ticket={
              'user':user_id,
              'longitude':context.user_data['location'].longitude,
              'latitude':context.user_data['location'].latitude,
              'photo':context.user_data['photo'],
              'type':TYPES[context.user_data['type']],
              'comment':context.user_data['comment'],
              #'donat': context.user_data['donat'],
              'created': date
              }
        r = requests.post(server_url+'api/tickets/', data = ticket)
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=reply_text, reply_markup=start_keyboard)
        return SELECTING_START
    else:
        reply_text='You can do it much better, I have no doubt about this ;-)'
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=reply_text, reply_markup=add_spot_keyboard)
        return CHOOSING
    
    
def start(update: Update, context: CallbackContext):
    reply_text='''Hi, I am Trashbin Bot. You can help me to clean up our beloved island, with your phone \n
    \n
Use \'Add spot\' button to pelengate some trash
    '''
    update.message.reply_text(reply_text, reply_markup=start_keyboard) 
    return SELECTING_START
                
    
#def done(update: Update, context: CallbackContext):
#    reply_text='Вам спсибо!'
#    update.message.reply_text(reply_text,reply_markup=ReplyKeyboardMarkup([['/new']], one_time_keyboard=True))
    
def stop(update: Update, _: CallbackContext) -> int:
    """End Conversation by command."""
    update.message.reply_text('Hope to see you soon :-*')

    return END

#def show_map(update: Update, context: CallbackContext) -> str:
#    print('qqq')
    
def show_ticket(update: Update, context: CallbackContext) -> str:
    table=[]
    if (context.user_data['comment'])and(context.user_data['location'])and(context.user_data['photo'])and(context.user_data['type']):
        table.append('Good job, You are ready to commit \:-D)\n')
    else:
        table.append('It would be really nice if you will pot crosses in the end of every line. You can do it, believe me ;) \n\n')
    for item in context.user_data:
        if context.user_data[item] == None:
            table.append(item+'\n')
        else:
            table.append(item+' +++\n')
    reply_text=''.join(table)
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=reply_text, reply_markup=add_spot_keyboard)
    return CHOOSING

def direct_donate(update: Update, context: CallbackContext) -> str:
    context.user_data['donat']=update.callback_query.data
    reply_text='Thanks a lot! You are awesome :)'
    #print(reply_text)
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=reply_text, reply_markup=add_spot_keyboard)
    return CHOOSING

def random_donate(update: Update, context: CallbackContext) -> str:
    context.user_data['random_donat']=context.user_data['random_donat']+1
    reply_text='''╭╭━━━╮╮┈┈┈┈┈┈┈┈┈┈
 ┈┃╭━━╯┈┈┈┈▕╲▂▂╱▏┈
 ┈┃┃╱▔▔▔▔▔▔▔▏╱▋▋╮┈
 ┈┃╰▏┃╱╭╮┃╱╱▏╱╱▆┃┈
 ┈╰━▏┗━╰╯┗━╱╱╱╰┻┫┈
 ┈┈┈▏┏┳━━━━▏┏┳━━╯┈
 ┈┈┈▏┃┃┈┈┈┈▏┃┃┈┈┈┈'''
    #print(reply_text)
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=reply_text, reply_markup=None)
    time.sleep(0.355)
    update.callback_query.edit_message_text(text="One more?", reply_markup=start_keyboard)
    return SELECTING_START

def show_spots(update: Update, context: CallbackContext) -> str:
    reply_text='not yet implemented :-('
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=reply_text, reply_markup=None)
    time.sleep(1)
    reply_text_2='''Hi, I am trashbin Bot. You can help me to clean up our beloved island, with your phone \n
    \n
Use \'Add spot\' button
    '''
    update.callback_query.edit_message_text(text=reply_text_2, reply_markup=start_keyboard)
    return SELECTING_START



#%% main
    
    
def run(updater):
    updater.start_polling()
    updater.idle()   
    
def main():
    mybot = Updater(TOKEN)
    dp = mybot.dispatcher
#%%add spot conver 2nd level
    data_selection_handlers = [
        
        CallbackQueryHandler(coordinates_chosen, pattern='^' + str(ADD_LOCATION) + '$'),
        CallbackQueryHandler(comment_chosen, pattern='^' + str(ADD_COMMENT) + '$'),
        CallbackQueryHandler(type_chosen, pattern='^' + str(CHOOSE_TYPE) + '$'),
        CallbackQueryHandler(photo_chosen, pattern='^' + str(ADD_PHOTO) + '$'),
        CallbackQueryHandler(complete, pattern='^' + str(SAVE_TICKET) + '$'),
        CallbackQueryHandler(show_ticket, pattern='^' + str(SHOW_TICKET) + '$'),
        CallbackQueryHandler(donate_chosen, pattern='^' + str(DIRECT_DONATE) + '$'),
        #CallbackQueryHandler(direct_donate, pattern='^' + str(DIRECT_DONATE) + '$'),
        
        #CallbackQueryHandler(start, pattern='^' + str(END) + '$'),
        ]
    add_spot_conversation=ConversationHandler(
        entry_points=[CallbackQueryHandler(add_spot, pattern='^' + str(ADD_SPOT) + '$')], 
        
        states={CHOOSING:data_selection_handlers,
                COORDINATES:[MessageHandler(Filters.location, add_location)],
                TYPE_JUNK:[CallbackQueryHandler(add_junk_type, pattern='^' + 'PLASTIC' + '$|^' + 'METAL'+ '$|^' + 'GLASS'+ '$|^' + 'ORGANIC' + '$')],
                PHOTO:[MessageHandler(Filters.photo, add_photo)],
                COMMENT:[MessageHandler(Filters.text, add_comment)],
                DONATE:[CallbackQueryHandler(direct_donate, pattern='^' + str(SMALL_D) + '$|^' + str(MEDIUM_D)+ '$|^' + str(LARGE_D) + '$')],
                },
                fallbacks=[CallbackQueryHandler(start, pattern='^' + str(END) + '$')],
                name='get data conv',
                allow_reentry=True)
#%%top level
    selection_handlers = [
        add_spot_conversation,
        CallbackQueryHandler(add_spot, pattern='^' + str(ADD_SPOT) + '$'),
        CallbackQueryHandler(random_donate, pattern='^' + str(DONATE) + '$'),
        CallbackQueryHandler(show_spots, pattern='^' + str(SHOW_SPOTS) + '$'),
    ]
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            
            SELECTING_START: selection_handlers,
            #SELECTING_ACTION: selection_handlers,
            ADD_SPOT: [add_spot_conversation],
            #STOPPING: [CommandHandler('start', start)],
        },
        fallbacks=[CommandHandler('stop', stop)],
    )
    
    
    
    dp.add_handler(conv_handler)
    run(mybot)

    
if __name__=='__main__':
    main()
