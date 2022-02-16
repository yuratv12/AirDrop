from collections import UserDict
import datetime
from itertools import count
import sqlite3

conn = sqlite3.connect("airdrop.db", check_same_thread=False)
cursor = conn.cursor()

def insert_new_user(chat_id, username, date_sub):
    sql = 'insert into users(chat_id, username, date_sub, balance, count_ref, nft)values\
(\'{0}\', \'{1}\', \'{2}\', \'0.0\', 0, 0);'.format(chat_id, username, date_sub)
    cursor.execute(sql)
    conn.commit()

def old_user(chat_id):
    sql = 'select * from users where chat_id = \'{0}\';'.format(chat_id)
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.commit()
    if result:
        return result

def add_user_wallet(chat_id, wallet):
    sql = 'update users set wallet = \'{0}\' where chat_id = \'{1}\';'.format(wallet, chat_id)
    cursor.execute(sql)
    conn.commit()


def add_coin_to_balance(chat_id, balance):
    sql = 'update users set balance = balance + {0} where chat_id = \'{1}\';'.format(balance, chat_id)
    cursor.execute(sql)
    conn.commit()


def add_refer(user_id, refer_id):
    sql = 'insert into refer_list(user_id, refer_id)values(\'{0}\', \'{1}\');'.format(refer_id, user_id)
    cursor.execute(sql)
    conn.commit()

def old_refer(chat_id, refer_id):
    sql = 'select * from refer_list where user_id = \'{0}\' and refer_id = \'{1}\';'.format(chat_id, refer_id)
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.commit()
    if result:
        return result

def get_count_refer_by_user(chat_id):
    sql = 'select count_ref from users where chat_id = \'{0}\';'.format(chat_id)
    cursor.execute(sql)
    result = cursor.fetchone()
    conn.commit()
    return result[0]

def get_last_gift(user_id):
    sql = 'select last_date from bonus where user_id = \'{0}\' order by last_date desc limit 1'.format(user_id)
    cursor.execute(sql)
    result = cursor.fetchone()
    conn.commit()
    if result:
        return result[0]
    else:
        return '2021-01-01 00:00:00'

def add_user_to_bonus(chat_id, drop_summ):
    sql = 'insert into bonus(user_id, last_date, drop_summ)values(\'{0}\', \'{1}\', \'{2}\');'.format(
        chat_id, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), drop_summ
    )
    cursor.execute(sql)
    conn.commit()

def get_user_balance(user_id):
    sql = 'select nft from users where chat_id = \'{0}\';'.format(user_id)
    cursor.execute(sql)
    result = cursor.fetchone()
    conn.commit()
    return result[0]

def user_balance_to_null(user_id):
    sql = 'update users set nft = 0 where chat_id = \'{0}\';'.format(user_id)
    cursor.execute(sql)
    conn.commit()

def get_user_status(user_id):
    sql = 'select status from users where chat_id = \'{0}\';'.format(user_id)
    cursor.execute(sql)
    result = cursor.fetchone()
    conn.commit()
    return result[0]

def select_count_user():
    sql = 'select count(*) from users'
    cursor.execute(sql)
    result = cursor.fetchone()
    conn.commit()
    return result[0]

def select_count_refer():
    sql = 'select count(*) from refer_list'
    cursor.execute(sql)
    result = cursor.fetchone()
    conn.commit()
    return result[0]

def get_all_sum_balanse():
    sql = 'select sum(balance) from users'
    cursor.execute(sql)
    result = cursor.fetchone()
    conn.commit()
    return result[0]

def update_count_refer(chat_id):
    sql = 'update users set count_ref = count_ref + 1 where chat_id = \'{0}\';'.format(chat_id)
    cursor.execute(sql)
    conn.commit()

def select_top_refer():
    sql = 'select chat_id, username, count_ref from users order by count_ref desc'
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.commit()
    return result

def get_all_chat_id():
    sql = 'select chat_id from users'
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.commit()
    list_chat = []
    for chat in result:
        list_chat.append(chat[0])
    return list_chat

def add_user_nft(user_id):
    sql = 'update users set nft = nft + 1 where chat_id = \'{0}\';'.format(user_id)
    cursor.execute(sql)
    conn.commit()

def get_nft_hist(user_id):
    sql = 'select max(sub) from nft_history where user = \'{0}\';'.format(user_id)
    cursor.execute(sql)
    result = cursor.fetchone()
    conn.commit()
    if result:
        return result[0]
    else:
        return 0

def add_info_nft_hist(user_id, count_ref):
    sql = 'insert into nft_history(user, sub)values(\'{0}\', \'{1}\');'.format(user_id, count_ref)
    cursor.execute(sql)
    conn.commit()
