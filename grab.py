import logging
from grab import Grab
import time
import re
import warnings

warnings.filterwarnings("ignore")

reg = re.compile('[^0-9 ]')

#Валидация номера
def validPhone(phone):
    if reg.sub('', phone) != '' and len(phone) >= 10:
        return True
    else:
        return False

#приведение к необходимому формату номера
def FormatPhone(phone):
    phone = phone.replace(' ', '')
    phone = phone.replace('-', '')
    phone = phone.replace('(', '')
    phone = phone.replace(')', '')
    phone = reg.sub('', phone)
    return phone

g = Grab(log_file='out.html')
g.go('https://vk.com')

#авторизация
g.doc.set_input('email', 'email') #логин для авторизации вк
g.doc.set_input('pass', 'pass') #пароль для авторизации вк
g.doc.submit('index_login_button')

error = 0 #счет ошибок на случай блокировки
offset = 490; #смещение в общем списке пользователей
page = 0 #количество страниц по 30 пользователей
#page - страница по 30 записей пользователей 1X (30 пользователей)
count_page = 1802 #всего пользователей в городе разделить на 30
phoneFound = False # флаг наден ли номер

f = open('script.sql', 'w')

while(page <= count_page):
    #поиск по стране и городу (мобильная версия)
    g.go('https://m.vk.com/search?c%5Bsection%5D=people&c%5Bname%5D=1&c%5Bcountry%5D=1&c%5Bcity%5D=1519&offset=' + str(offset));
    users = g.xpath_list('//div[@class="si_body"]//span')
    link = g.xpath_list('//a[@class="simple_fit_item search_item"]')
    i = 0
    for element in link:
        g.go('https://vk.com' + element.get('href'))
        
        #проверка, есть ли на странице контактные данные и номер
        if g.doc.text_search(u'Контактная информация') and g.doc.text_search(u'Моб. телефон:'):
            try:
                phone = FormatPhone(g.xpath('//div[@id="profile_full"]//div[2]//div[2]//div[1]//div[2]').text_content())
                if validPhone(phone):
                    username = g.tree.xpath('//title/text()')[0]
                    phoneFound = True
                else:
                    phoneFound = False
            except IndexError:
                error = error + 1
                phoneFound = False

        #Если номер найден, то найти остальные данные
        if phoneFound:
            if g.doc.text_search(u'День рождения:'):
                try:
                    birthday = g.xpath('//div[@id="profile_short"]/div[1]/div[2]').text_content()
                except IndexError:
                    birthday = "";
            if g.doc.text_search(u'Город:'):
                try:
                    city = g.xpath('//div[@id="profile_short"]/div[2]/div[2]/a').text_content()
                except IndexError:
                    city = "";
            if g.doc.text_search(u'Instagram:'):
                try:
                    instagram = g.xpath('//div[@id="profile_full"]/div[2]/div[2]/div[2]/div[2]/a').text_content()
                except IndexError:
                    instagram = "";
            else:
                instagram = "-"
            f.write(username + ' (' + birthday + ') ' + ' ' + city + ' - ' + phone + ' inst: ' + instagram + ' vk: ' + element.get('href'))
            print(username + ' (' + birthday + ') ' + ' ' + city + ' - ' + phone + ' inst: ' + instagram + ' vk: ' + element.get('href'))
        else:
            print(str(i) + " - ")

        phoneFound = False
        
        i = i + 1
        time.sleep(15)
        
    if error == 20:
        time.sleep(1200)
        error = 0
        break
    
    offset = offset + 30
    page = page + 1
    print('page: ' + str(page))
    print('offset: ' + str(offset))
    
f.close()
print('Ready')