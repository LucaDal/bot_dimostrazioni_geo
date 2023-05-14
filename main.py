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
num_dim = 28


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


@bot.message_handler(commands=['start'])
def get_help(message):
    help_info(message)


@bot.message_handler(commands=['lista'])
def get_lista(message):
    lista = ""
    for dim in get_list_dim():
        lista = "{}{}".format(lista, dim)
    bot.send_message(message.chat.id, lista)


@bot.message_handler(commands=['help'])
def help_info(message):
    string = "Comandi:\n" \
             "/nuova\nPrende una dimostrazione che ancora non hai fatto.\n_________\n" \
             "/setDif <id dimostrazione>\nSetta la dimostrazione come difficile - se gia settata come difficile -> " \
             "la rimette normale.\n_________\n" \
             "/randomDif\nPrende una dimostrazione random che hai settato come difficile.\n_________\n" \
             "/random\n" \
             "Una dimostrazione random, fatta o non fatta.\n_________\n"\
             "/reset\nRipristina tutte le dimostrazioni fatte.\n_________\n"\
             "/lista\nLista di tutte le dimostrazioni.\n_________\n"\
             "/listaDif\nLista di tutte le dimostrazioni settate Difficili."
    bot.send_message(message.chat.id, string)


@bot.message_handler(commands=['setDif'])
def set_dif(message):
    conn = is_connection_all_right(message.chat.id)
    if conn is None:
        return
    list_message = get_list_from_message(message)
    if len(list_message) == 0:
        bot.send_message(message.chat.id, "Inserisci l'id della dimostrazione {1-28}")
        return
    id_dim = list_message[0]
    if is_value_correct(id_dim):
        if db.update_user_difficulty(conn, message.from_user.id, int(id_dim)-1):
            bot.send_message(message.chat.id, "Dim {} -> difficile".format(id_dim))
        else:
            bot.send_message(message.chat.id, "Dim {} -> normale".format(id_dim))
    else:
        bot.send_message(message.chat.id, "Inserisci l'id della dimostrazione {1-28}")


def get_list_from_message(message):
    string = get_string_from_message(message)
    string_split = str.split(string)
    listToReturn = []
    for string in string_split:
        listToReturn.append(string)
    return listToReturn


def get_string_from_message(message):
    myList = list(message.text)
    mySecondList = []
    startInserting = False
    for i in myList:
        if startInserting:
            mySecondList.append(i)
        if startInserting is False and i == ' ':
            startInserting = True
    newMessage = str.join("", mySecondList)
    return newMessage


def is_value_correct(value):
    if value.isnumeric():
        val = int(value)
        if val <= 0 or val > num_dim:
            return False
        return True
    else:
        return False


@bot.message_handler(commands=['listaDif'])
def lista_dif(message):
    conn = is_connection_all_right(message.chat.id)
    if conn is None:
        return
    lista = ""
    list_id_dim_difficult = get_list_dim_from_db(db.get_difficult_dim(conn, message.from_user.id))
    if len(list_id_dim_difficult) == 0:
        bot.send_message(message.chat.id, "Nessuna dimostrazione segnata come difficile")
        return
    lista_dim = get_list_dim()
    for val in list_id_dim_difficult:
        lista = "{}{}".format(lista,lista_dim[val])
    bot.send_message(message.chat.id, lista)


@bot.message_handler(commands=['randomDif'])
def random_dif(message):
    conn = is_connection_all_right(message.chat.id)
    if conn is None:
        return
    list_id_dim_difficult = get_list_dim_from_db(db.get_difficult_dim(conn, message.from_user.id))
    if len(list_id_dim_difficult) == 0:
        bot.send_message(message.chat.id, "Nessuna dimostrazione segata come difficile")
    else:
        bot.send_message(message.chat.id,
                         get_list_dim()[list_id_dim_difficult[random.randint(0, len(list_id_dim_difficult) - 1)]])


def get_list_dim_from_db(tuple_dim) -> list:
    list_id_dim = []
    for val in tuple_dim:
        list_id_dim.append(val[0])
    return list_id_dim


def get_num_from_undone_dim(conn, id_user) -> str:
    list_dim_done = db.get_done_dim(conn, id_user)
    list_all_dim = get_list_dim()
    if list_dim_done is None:
        rand_int = random.randint(0, len(list_all_dim) - 1)
        db.insert_user_dim_into_db(conn, id_user, rand_int)
        return list_all_dim[rand_int]
    id_dim_to_do = []
    list_int_done = get_list_dim_from_db(list_dim_done)
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
    with open("dim analisi2.txt", 'r') as file:
        for line in file:
            dim.append(line)
    return dim


bot.infinity_polling(timeout=10, long_polling_timeout=5)
