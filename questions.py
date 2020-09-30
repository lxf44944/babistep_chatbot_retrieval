##由商品类别+联想动植物+商品信息名称 录入问题
import pymysql
import csv
import re
import codecs
import pandas as pd
import numpy as np
import os,django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE','fire.settings')


def get_conn():
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='mysqlroot', db='huohuo', charset='utf8')
    return conn



def read_csv_to_mysql(filename):
    creg = "[^A-Za-z\u4e00-\u9fa5]"
    nreg = "[^0-9A-Za-z\u4e00-\u9fa5]"
    pdata = pd.read_csv(filename,usecols=['name','fdName','leibie','cat','url','price'])
    cat = pd.read_csv('/Users/liyijie/GitHub/babistep_retrieval-based/creatures.csv')   # 读取动植物列表
    ccategory = cat.columns                                                              # 获取表头
    ccat = {} 
    ccatcopy = {}                                                                         # 把表头以字典形式存储
    p=0
    for c in ccategory:
        ccat[p] = re.sub(creg, ' ', c).lower()
        ccatcopy[p] = str(ccat[p]).replace(' ','')
        p=p+1
    numofpdata = pdata.shape[0]
    stores = pdata['fdName']
    leibie = pdata['leibie']
    category = pdata['cat']
    dicat = {}
    dicatcopy = {}
    i=0
    for c in category:
        dicat[i] = re.sub(creg, ' ', c).lower()
        dicatcopy[i] = str(dicat[i]).replace(' ','')
        i=i+1
    names = pdata['name']
    nicat = {}
    j=0
    for n in names:
        nicat[j] = re.sub(nreg, ' ', n)
        j=j+1
    gift = pdata['url']
    prices = pdata['price']
    maxprs = {}
    for a in range(p):
        maxprs[ccatcopy[a]] = [0,0]
    minprs = {}
    for b in range(p):
        minprs[ccatcopy[b]] = [9999999999,0]
    
    for n in range(numofpdata):
        if(prices[n] > maxprs[dicatcopy[n]][0]):
            maxprs[dicatcopy[n]][0] = prices[n]
            maxprs[dicatcopy[n]][1] = n
        if(prices[n] < minprs[dicatcopy[n]][0]):
            minprs[dicatcopy[n]][0] = prices[n]
            minprs[dicatcopy[n]][1] = n

    for e in range(p):
        print(maxprs[ccatcopy[e]][1])
        print(minprs[ccatcopy[e]][1])
        nicat[maxprs[ccatcopy[e]][1]] += 'the most expensive with the highest price'
        nicat[minprs[ccatcopy[e]][1]] += 'the cheapest with the lowest price'
        
    conn = get_conn()
    cur = conn.cursor()
    
    sql = "delete from polls_answer where id > 0"
    cur.execute(sql)
    
    sql = "delete from polls_question where id > 0"
    cur.execute(sql)


    for m in range(numofpdata):
        question = stores[m]+' '+dicat[m]+' '+leibie[m]+' '+nicat[m]
        sql = 'insert into polls_question(id, question_text, pub_date, votes) values(%s, %s, %s, %s)' 
        cur.execute(sql,(m+1,str(question.lower()),str(timezone.now()),0))
        answer = gift[m]#只要url
        sql = 'insert into polls_answer(id, answer_text, votes, question_id) values(%s, %s, %s, %s)' 
        cur.execute(sql,(m+1,str(answer.lower()),0,m+1))

    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    read_csv_to_mysql('product03.csv')