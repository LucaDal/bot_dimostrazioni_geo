import os
import telebot
import dataBase as db
import random
import json

file = open(".env", "r")
env = json.load(file)
KEY_TOKEN = env['KEY_TOKEN']
bot = telebot.TeleBot(KEY_TOKEN)
file.close()


def is_connection_all_right(chat_id):
    """
    :param message:
    :return: False id something fails, the connection instead
    """
    conn = db.create_connection()
    if conn is None:
        bot.send_message(chat_id, "Problems with data base, contact @LucaDalessandro")
        return False
    return conn


@bot.message_handler(commands=['lista'])
def get_lista(message):
    lista = ""
    for dim in get_list_dim():
        lista = "{}{}".format(lista, dim)
    bot.send_message(message.chat.id, lista)


@bot.message_handler(commands=['help'])
def info(message):
    bot.send_message(message.chat.id, "Vivo")


def get_num_from_undone_dim(conn, id_user) -> str:
    list_dim_done = db.get_done_dim(conn, id_user)
    list_all_dim = get_list_dim()
    if list_dim_done is None:
        rand_int = random.randint(0, len(list_all_dim) - 1)
        db.insert_user_dim_into_db(conn, id_user, rand_int)
        return list_all_dim[rand_int]
    id_dim_to_do = []
    list_int_done = []
    for val in list_dim_done:
        list_int_done.append(val[0])
    for i in range(len(list_all_dim)):
        if i not in list_int_done:
            id_dim_to_do.append(i)
    if len(id_dim_to_do) == 0:
        return "Hai fatto tutte le dimostrazioni almeno una volta!\nresetta con /reset "
    rand_int = random.randint(0, len(id_dim_to_do) - 1)
    db.insert_user_dim_into_db(conn, id_user, id_dim_to_do[rand_int])
    return list_all_dim[id_dim_to_do[rand_int]]


@bot.message_handler(commands=['nuova'])
def print_dim(message):
    conn = is_connection_all_right(message.chat.id)
    if conn is None:
        return
    dim = get_num_from_undone_dim(conn, message.from_user.id)
    bot.send_message(message.chat.id, dim)


@bot.message_handler(commands=['reset'])
def reset(message):
    conn = is_connection_all_right(message.chat.id)
    if conn is None:
        return
    db.delete_user_dim(conn, message.from_user.id)
    bot.send_message(message.chat.id, "oky, ripristinate tutte le dimostrazioni!")


@bot.message_handler(commands=['random'])
def random_dim(message):
    conn = is_connection_all_right(message.chat.id)
    if conn is None:
        return
    list_all_dim = get_list_dim()
    dim = get_num_from_undone_dim(conn, message.from_user.id)
    bot.send_message(message.chat.id, list_all_dim[random.randint(0, len(list_all_dim) - 1)])


def get_list_dim():
    dim = []
    with open("dimostrazioni.txt", 'r') as file:
        for line in file:
            dim.append(line)
    return dim


bot.infinity_polling(timeout=10, long_polling_timeout=5)
