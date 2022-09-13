# plugins init
from os import system as cmd
import configparser
import pyrebase
import json
import plugins
import pyfiglet
import aiogram
import pyfiglet
import logging
from colorama import Fore, Style
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from os import path
import platform
import random
import requests
import sys
import re
import urllib3
import json
from bs4 import BeautifulSoup
import ast

# Configure cmd clear command

cmd_clear = plugins.cfg_cmd_clear(platform.system())

# Configure cfg file

config = configparser.ConfigParser()
config.read("cfg.ini", encoding="utf-8")

# Configure ApiToken

API_TOKEN = config['BOT_SETTINGS']['token']

# Configure get headers

headers_Get = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load database as writeable

if path.isfile('states.json') is False:
    raise Exception("Statesdb is not found!")


# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def welcome():
    name_bot = config['BOT_SETTINGS']['name']
    print(Fore.GREEN + 'Welcome ' + Fore.LIGHTRED_EX + "to:\n" + Style.RESET_ALL)
    print(pyfiglet.figlet_format(name_bot))
    print(Fore.RED + 'Private bot by greendevilll'+ Style.RESET_ALL)
    if path.isfile('states.json') is False:
        raise Exception("Statesdb is not found!")
    with open('states.json', 'r') as internalJson:
        statesDatabase = json.load(internalJson)


def main():
    welcome()

    async def sendAdmins(product, phone):
        for admin in config["MODERATORS_LIST"]:
            adminid = config["MODERATORS_LIST"][admin]
            await bot.send_message(adminid,f"Новая заявка:\nТовар: {product}\nТелефон для связи: {phone}")

    async def syncDb(user_id, state):
        #try:
        with open('states.json', 'r') as fp:
            statesDatabase = json.load(fp)
        
        try:
            model = statesDatabase[str(user_id)]["model"]
            contributor = statesDatabase[str(user_id)]["contributor"]
            statesDatabase[str(user_id)].update(
                {
                    "model":model,
                    "contributor":contributor,
                    "state":state
                }
            )
            json.dump(statesDatabase, open('states.json','w'))
        except KeyError:
            statesDatabase.update(
                {
                    user_id: {
                        "state": 0,
                        "model": 0,
                        "contributor": 0
                    }
                }
            )
            json.dump(statesDatabase, open('states.json', 'w'))
        """except KeyError:
            print("KEY ERROR [debug]")
            with open('states.json', 'r') as fp:
                statesDatabase = json.load(fp)
            statesDatabase.update(
                {
                    user_id: {
                        "state": 0,
                        "model": 0,
                        "contributor": 0
                    }
                }
            )
            json.dump(statesDatabase, open('states.json', 'w'))"""

    async def addToDb(user_id, key, data):
        with open('states.json', 'r') as fp:
            statesDatabase = json.load(fp)
        model = statesDatabase[str(user_id)]["model"]
        state = statesDatabase[str(user_id)]["state"]
        contributor = statesDatabase[str(user_id)]["contributor"]
        statesDatabase.update(
            {
                str(user_id): {
                    "model": model,
                    "contributor": contributor,
                    "state": state,
                    key:data
                }
            }
        )
        json.dump(statesDatabase, open('states.json','w'))

    @dp.message_handler(commands=["start", "help"])
    async def main_page(message: types.Message, callback_query: types.CallbackQuery = None):
        await syncDb(message.from_user.id, 0)
        keyboard = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton(str(config['BOT_PHRASE']['findbtn']), callback_data='sending')
        btn2 = InlineKeyboardButton(str(config['BOT_PHRASE']['idkbtn']), callback_data='idkback')
        keyboard.add(btn1, btn2)
        await message.reply(
            str(config['BOT_PHRASE']['greetings']),
            reply_markup=keyboard)

    @dp.message_handler(chat_type=types.ChatType.PRIVATE)
    async def private_filterFinder(message: types.Message, callback_query: types.CallbackQuery = None):
        with open('states.json', 'r') as fp:

            statesDatabase = json.load(fp)

        print()
        if statesDatabase[str(message.from_user.id)]["state"] == "iKnow":
            text = message.text
            by_number = text.split()
            tupoi = await find_onsite("%20".join(by_number))
            linksProduct = tupoi['links']
            productNames = tupoi['products']
            cityNames = tupoi['city']
            builderNames = tupoi['builder']
            stockNames = tupoi['stock']
            outputNeed = []
            message_text = f'Найдено {len(linksProduct)} товаров:\n'
            if message_text == 'Найдено 0 товаров:\n':
                message.reply('Ничего не найдено.')
            else:
                strOutput = 0
                for productName in productNames:
                    productIndex = productNames.index(productName)
                    productLink = linksProduct[productIndex]
                    cityOutput = cityNames[productIndex]
                    builderOutput = builderNames[productIndex]
                    stockOutput = stockNames[productIndex]

                    strOutput = f'{productName} : {productLink}'
                    message_text = f'{message_text}\n{strOutput}; {stockOutput} в {cityOutput}; Произведено {builderOutput}\n'
                if len(message_text) > 4096:
                    for x in range(0, len(message_text), 4096):
                        await message.reply(message_text[x:x + 4096])
                else:
                    await message.reply(message_text)

        elif statesDatabase[str(message.from_user.id)]["state"] == "idk1":
            await syncDb(message.from_user.id, "idk2")
            await addToDb(message.from_user.id, "contributor", message.text)
            await message.reply("Укажите модель техники!")
        elif statesDatabase[str(message.from_user.id)]["state"] == "idk2":
            await syncDb(message.from_user.id, "idk3")
            await addToDb(message.from_user.id, "model", message.text)
            await message.reply("Принято! Пожалуйста, укажите свой номер телефона для связи.")
        elif statesDatabase[str(message.from_user.id)]["state"] == "idk3":
            phone = message.text
            with open('states.json', 'r') as fp:
                statesDatabase = json.load(fp)

            model = statesDatabase[str(message.from_user.id)]["model"]
            contributor = statesDatabase[str(message.from_user.id)]["contributor"]

            await addToDb(message.from_user.id, phone, message.text)
            await sendAdmins(f'{model} от компании {contributor}', phone)

    @dp.message_handler()
    async def checker(message: types.Message, callback_query: types.CallbackQuery = None):
        by_number = message.text.split()
        print(message.text)
        if "куплю" in by_number or "Куплю" in by_number or "спрос" in by_number or "Спрос" in by_number:
            from_users = message.from_user.id
            chat_id = message.chat.id
            print(f'{from_users}\n{chat_id}')
            for validate in by_number:
                if "!куплю" == validate or "!Куплю" == validate:
                    by_number.pop(by_number.index(validate))
                    break
            tupoi = await find_onsite("%20".join(by_number))
            linksProduct = tupoi['links']
            productNames = tupoi['products']
            cityNames = tupoi['city']
            builderNames = tupoi['builder']
            stockNames = tupoi['stock']
            outputNeed = []
            message_text = f'Найдено {len(linksProduct)} товаров:\n'
            print(chat_id)
            strOutput = 0
            for productName in productNames:
                productIndex = productNames.index(productName)
                productLink = linksProduct[productIndex]
                cityOutput = cityNames[productIndex]
                builderOutput = builderNames[productIndex]
                stockOutput = stockNames[productIndex]

                strOutput = f'{productName} : {productLink}'
                message_text = f'{message_text}\n{strOutput}; {stockOutput} в {cityOutput}; Произведено {builderOutput}\n'
            if chat_id == from_users:
                await message.reply(message_text)
            else:
                await message.reply('Отправил в личные сообщения!')
                await bot.send_message(from_users, message_text)

    @dp.callback_query_handler(lambda c: c.data == "idkback")
    async def idk_finder(callback_query=types.CallbackQuery):
        await syncDb(callback_query.from_user.id, "idk1")
        await callback_query.message.reply('Отлично! Назовите марку техники.')

    @dp.callback_query_handler(lambda c: c.data == "sending")
    async def private_chatFinder(callback_query=types.CallbackQuery):
        await syncDb(callback_query.from_user.id, "iKnow")
        await callback_query.message.reply(
            '💬 Для того чтобы найти запчасть, скиньте мне название или товарный номер запчасти.')

    async def find_onsite(name_of_order):
        query = {
            's': name_of_order
        }
        req = requests.get(f'https://gcrichtone.com/', params=query)
        soup = BeautifulSoup(req.text, 'html.parser')
        allProducts = soup.findAll('div', class_='ct-container')
        linksProduct = []
        productNames = []
        cityNames = []
        stockNames = []
        builderNames = []
        for links in allProducts:
            h2_section = links.findAll('h2', class_='entry-title')
            for link in h2_section:
                tag_a = link.find('a')
                linka = tag_a.get('href')
                city, stock, builder = await getStock(linka)
                linksProduct.append(linka)
                productNames.append(tag_a.text)
                cityNames.append(city)
                stockNames.append(stock)
                builderNames.append(builder)
        returnList = {
            'links': linksProduct,
            'products': productNames,
            'city': cityNames,
            'builder': builderNames,
            'stock': stockNames
        }
        return returnList

    async def getStock(link):
        req = requests.get(link)
        soup = BeautifulSoup(req.text, 'html.parser')
        city = 0
        stock = 0
        builder = 0
        for data2 in soup.findAll('p', class_='stock in-stock'):
            stock = data2.text
        for data in soup.findAll('table', class_='woocommerce-product-attributes shop_attributes'):
            for cityData in data.findAll('tr',
                                         class_='woocommerce-product-attributes-item woocommerce-product-attributes-item--attribute_pa_gorod'):
                for cityDataText in cityData.findAll('td', class_='woocommerce-product-attributes-item__value'):
                    for cityDataH in cityDataText.find('p'):
                        city = cityDataH
            for builderData in data.findAll('tr',
                                            class_='woocommerce-product-attributes-item woocommerce-product-attributes-item--attribute_pa_manufacturer'):
                for builderDataText in builderData.findAll('td', class_='woocommerce-product-attributes-item__value'):
                    for builderDataH in builderDataText.find('p'):
                        builder = builderDataH

        return city, stock, builder


if __name__ == "__main__":
    cmd(cmd_clear)
    main()
    executor.start_polling(dp, skip_updates=True)
