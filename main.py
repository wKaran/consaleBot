import telegram.ext
import requests
from bs4 import BeautifulSoup
import json, os
from dotenv import load_dotenv, dotenv_values

load_dotenv()
Token = os.getenv('consale_APIKey')

Headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"}

with open('users.json', 'r') as file:
    _users = json.load(file)     #users.json is Json database of users, _users is local replica of original json file.

def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    update.message.reply_text('''Welcome to Consale!
We'll keep you in the loop whenever the prices of PS5 or Xbox Series X drop. 
Just sit back, relax, and let us do the hunting!
                              
click /help to get helping menu.''')
    chat_id = update.message.chat_id

    if chat_id not in _users["Users"]:
        _users["Users"].append(chat_id)
        with open("users.json", 'w', encoding='utf-8') as file:
            json.dump(_users, file, ensure_ascii=False, indent=4) #update json file after adding new user.

def help(update: telegram.Update, context: telegram.ext.CallbackContext):
    update.message.reply_text('''Consale Help Menu!
Need a hand? We've got you covered! Here's how you can make the most of Consale: 
                              
  /start - Begin your journey with Consale!
  /status - Check which consoles you're tracking and current prices.
  /help - Get back to this handy guide anytime
                              
Got Query? contact @karanxingh (Spamming will lead to account block)''')

#------------------------------------------------------------------ PriceUpdate code --------------------------------------------------------------------------------------------------
def priceUpdate(context:telegram.ext.CallbackContext):
    with open('products.json', 'r') as file:
        Products = json.load(file)

    with open('users.json', 'r') as file:
        users = json.load(file)

    change = False

    for name, product in Products.items():
        amazon_page = requests.get(product["Amazon"], headers=Headers)
        #flipkart_page = requests.get(product["flipkart"], headers=Headers)
        soup = BeautifulSoup(amazon_page.content,'html.parser')
        price_whole = str(soup.find('span', {'class': 'a-price-whole'}).get_text())    # The whole part of the price
        price_whole = int(price_whole.replace(',','').rstrip('.'))
        
        if price_whole < product["price"]:
            product["price"] = price_whole
            change = True

            message = f'{name} price has dropped. Buy it now from "{product['Amazon']}"'
            for chat_id in users["Users"]:                                                 #to get fresh list of users
                context.bot.send_message(chat_id=chat_id, text=message)       
        
        elif price_whole > product["price"]:
            product["price"] = price_whole
            change = True

    if change:
        with open("products.json", 'w', encoding='utf-8') as file:
            json.dump(Products, file, ensure_ascii=False, indent=4)

#-----------------------------------------------------priceUpdate endhere--------------------------------------------------------------------

with open('products.json', 'r') as file:      #to get fresh json database of products 
        Products = json.load(file)

def status(update: telegram.Update, context: telegram.ext.CallbackContext):
    for name, product in Products.items():
        message = f"{name} costs {product['price']}. Buy from '{product["Amazon"]}'"
        context.bot.send_message(chat_id=update.effective_chat.id, text= message)
    update.message.reply_text('Need more consoles in the list. Contact @Karanxingh')

def main():

    updater = telegram.ext.Updater(Token, use_context=True)
    dispatch = updater.dispatcher

    dispatch.add_handler(telegram.ext.CommandHandler('start', start))
    dispatch.add_handler(telegram.ext.CommandHandler('help', help))
    dispatch.add_handler(telegram.ext.CommandHandler('status', status))

    job_queue = updater.job_queue
    job_queue.run_repeating(priceUpdate, interval=66, first=0)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()