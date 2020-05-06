#!/usr/bin/python3
import requests, datetime, time, pprint, telebot, os
from bs4 import BeautifulSoup
import pandas as pd
from openpyxl import load_workbook

token = '827576612:AAEX0IHqMW5x-oWrh8T1ZXhE-9_K8pXMTJ0'
bot = telebot.TeleBot(token)

path_files = '/home/pi/Documents/Python/'
url = 'https://www.avito.ru/novosibirsk/mototsikly_i_mototehnika/mototsikly-ASgBAgICAUQ80k0?user=1&radius=0&q=мотоцикл&i=1'
df = pd.DataFrame(columns=['ID', 'Дата', 'Заголовок', 'Цена', 'Добавлено', 'Расположение', 'Ссылка'])
c = 0 

def sheet_analitics():
    sheet1 = pd.read_excel(path_files + 'moto/{}'.format(get_last_couple_sheet()[0]))
    sheet2 = pd.read_excel(path_files + 'moto/{}'.format(get_last_couple_sheet()[1]))
    sheet1 = sheet1.drop_duplicates(subset='ID')
    sheet2 = sheet2.drop_duplicates(subset='ID')
    del sheet1['Unnamed: 0']
    del sheet2['Unnamed: 0']
    merge_sheet = sheet1.merge(sheet2, how='outer', left_on='ID', right_on='ID')
    m1 = merge_sheet[merge_sheet['Заголовок_y'].isnull()]
    sold = m1[['Заголовок_x', 'Цена_x', 'Добавлено_x',
           'Расположение_x', 'Ссылка_x']]
    m2 = merge_sheet[merge_sheet['Заголовок_x'].isnull()]
    appearance = m2[['Заголовок_y', 'Цена_y', 'Добавлено_y',
           'Расположение_y', 'Ссылка_y']]
    
    sold_str = ''
    appearance_str = ''
    
    appearance_str += 'Появилось или обновлено: {} новых объявлений \n'.format(len(appearance))
    sold_str += 'Сняты с публикации {} объявлений\n'.format(len(sold))

    file_name_appearance = path_files + 'moto_renew/moto_appearance {}.xlsx'.format(datetime.datetime.today().strftime("%d.%m.%Y %H-%M"))
    file_name_sold = path_files + 'moto_renew/moto_sold {}.xlsx'.format(datetime.datetime.today().strftime("%d.%m.%Y %H-%M"))
                                                                          
    appearance.to_excel(file_name_appearance)
    sold.to_excel(file_name_sold)
    
    return sold_str + appearance_str, file_name_sold, file_name_appearance

def get_amount_pages():
    html = requests.get(url,
                       headers={
                           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3149.47 Safari/537.36',
                           'Accept-Language': 'ru'
                       })
    soup = BeautifulSoup(html.text, 'html.parser')
    return int(soup.find_all(class_='pagination-root-2oCjZ')[0].find_all('span')[-2].text)

def parse_page(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'lxml')
    item_list = soup.find_all(class_='item__line')
    global c
    date = datetime.datetime.today()
    for i in item_list:
        try:
            price = int(''.join(i.find(class_='snippet-price-row').text.strip().split()[:-1]))
        except:
            price = 0  
            
        title = i.find(class_='snippet-link').text # Заголовок
        try:
            location = i.find(class_='item-address-georeferences-item__content').text
        except:
            location = 'Не указано'
        link = 'https://www.avito.ru' + i.find('a', class_='snippet-link')['href']   
        added = i.find(class_='snippet-date-info').text.strip()
        id_ = int(link.split('_')[-1])
        df.loc[c] = {'ID':id_, 'Дата':date, 'Заголовок':title, 'Цена':price, 'Добавлено': added, 'Расположение':location, 'Ссылка':link}
        c += 1
          
for i in range(1, get_amount_pages()+1):
    page_url = url + '&p={}'.format(i)
#    time.sleep(3)
    parse_page(page_url)

df = df[df['Цена'].astype('str').str.isdecimal()]
df = df[(df['Цена'] > 30000)]
df = df.drop_duplicates(subset='ID')

# text_for_bot = '''Парсинг мотоциклов в Новосибе {}
# Средняя цена:  {} p
# Медиана: {} p
# Количество объявлений: {} шт

# {}
# '''.format(datetime.datetime.today().strftime("%d.%m.%Y %H-%M"), 
#            int(df['Цена'].mean()), 
#            df['Цена'].median(), 
#            len(df),
#            sheet_analitics()[0])

df.to_csv('all_moto.csv', mode='a', header=False)

'''common_df = pd.read_csv('/home/pi/Documents/Python/all_moto.csv', index_col=0)
add_df = pd.read_excel(file_name)
add_df['Дата'] = ' '.join(os.listdir(file_name)[0][:-5].split()[1:])
common_df = common_df.append(3333, ignore_index=True)
common_df.to_csv('/home/pi/Documents/Python/all_moto.csv')'''

# print(text_for_bot)
bot.send_message(-486279980, 'Парсинг прошёл успешно, данные записаны в базу данных')

# sold_send = open(sheet_analitics()[1], 'rb')
# appearance_send = open(sheet_analitics()[2], 'rb')

# bot.send_document(-486279980, sold_send)
# bot.send_document(-486279980, appearance_send)
