#!/usr/bin/pypy3 -u
from pyrogram           import Client, MessageHandler, Filters, ChatMember
from time               import sleep as sleep
from threading          import Thread
import random
import shelve
import time

from config             import api_id, api_hash, nyanpasu_un, nyanpasu_id, katsu_id
from words.service      import lang_service
from funcs.rep          import user_make, user_rep_change
from funcs.speechrec    import speech_recognition
from funcs.chat_db      import ChatDB as chat_db
from funcs.delete       import del_nyanpasu
from funcs.functions    import functions
from funcs.mood         import mood_func
from funcs.replaier     import replaier
from funcs.adminctl     import adminctl
from funcs.chat_db      import User
from funcs.ship         import ship
from funcs.roleplay     import roleplay


with shelve.open('DB') as db:
    app = Client("hebushek", api_id, api_hash)

    @app.on_message((Filters.group | Filters.private))
    def nyanpasu(Client, message):
        k = str(katsu_id)
        n = str(nyanpasu_id)
        chat_id = str(message.chat.id)
        mmbr =  message.from_user
        reply = message.reply_to_message
        if reply:
            reply_user     =    message.reply_to_message.from_user
            reply_user_id  =    reply_user.id
            reply_usrname  =     ('@' + str(reply_user.username)) if reply_user.username else reply_user.first_name
            msg_id         =    int(reply.message_id)
        else:
            reply_user     =    None
            reply_user_id  =    None
            reply_usrname  =    None
            msg_id         =    int(message.message_id)

        if chat_id not in db:
            db[chat_id] = chat_db()
        chat    = db[chat_id]

        msb = str(message.text)
        msg = msb.lower()
        msgs = msg.split()

        service = lang_service(chat)
        chat.mood = mood_func(chat)
        user_make(message, chat, service)
        
#        nyanpasu_mmbr = app.get_chat_member(chat_id, nyanpasu_id)
#        nyanpasu_stat = nyanpasu_mmbr.status
#        if user.status is 'administrator' or 
#            user.status is 'creator' or 
#            mmbr.id == k or mmbr.id == n:
#            if nyanpasu_stat is 'administrator' or 
#                nyanpasu_stat is 'creator':
#        usrname  = ('@' + str(message.from_user.username)) if message.from_user.username else message.from_user.first_name

        if message.voice:
            print('voice at '+str(chat_id)+' - '+str(message.message_id))
            speech_recognition(app, service, chat_id, message, chat.lang)

        elif message.new_chat_members:
            if str(mmbr.id) ==  n:
                txt = """Приветствую всех, 
Чтобы настроить приветственное сообщение
введите "!config greet on" и "!config greet текст".
Чтобы включить ответчик введите "!config cond on"."""
                message.reply(txt)
            elif chat.greetc == 1: 
                txt = chat.greet
                message.reply(txt)
            print('greeted at '+str(chat_id)+' - '+str(message.message_id))

        elif ('!rma ' in msg or '!rmh ' in msg or '!рма ' in msg or '!рмх ' in msg):
            if mmbr.id == katsu_id or mmbr.id == nyanpasu_id:
                del_nyanpasu(app, chat_id, mmbr, msgs)
                print('deleted msgs at '+str(chat_id)+' - '+str(message.message_id))

        elif '!' in msgs[0]:
            functions(app, message, chat, service, reply_usrname)
            if 'debug' in msg:    print(message)

        elif '/' in msgs[0]:
            roleplay(app, nyanpasu_id, msgs[0], chat_id, message.text, message.message_id, message.from_user.first_name)
        
        elif '!config' in msg:
            adminctl(app, message, chat, service)

        elif chat.cond == 1 and chat.users[mmbr.id].cond == 1:
            if (reply_user_id == n or reply == None):
                replaier(chat, app, chat_id, msg, msg_id)

        elif chat.cond == 0 or chat.users[mmbr.id].cond == 0:
            if (reply_user_id == n or nyanpasu_un in msg):
                replaier(chat, app, chat_id, msg, msg_id)
        
        elif reply_user_id:
            user_rep_change(message, chat, reply_user_id, service, rep_usr_name)
        
#        elif message.chat.type == 'private':
#                replaier(chat, message)

        db[chat_id] = chat
        db.sync()
    
    app.run()