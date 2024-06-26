import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

def get_fresh_hrefs(url, retries=5):
    err = ""
    while retries >= 0:
        try:
            resp = requests.get(url)
            soup = BeautifulSoup(resp.content, 'html.parser')
            items = soup.find_all('div', class_='list-item')
            hrefs = [item.find('a', itemprop='url')['href'] for item in items]
            return hrefs

        except Exception as e:
            err = e
            retries -= 1
    print(f'Ошибка при извлечении ссылок на новости: {err}. url: {url}')
    return None
    
def get_card(url, last_update, retries=5):
    err = ""
    while retries >= 0:
        try:
            resp = requests.get(url)
            soup = BeautifulSoup(resp.content, 'html.parser')
            content = soup.find('div', class_='endless__item')
            ts = content["data-pts"]
            if int(ts) > last_update:
                title = content.find('div', itemprop='headline').text
                annot = content.find('div', itemprop='description').text
                author = content.find('div', itemprop='author').find('div', itemprop='name').text.strip()
                body = content.find('div', itemprop='articleBody').text
                return {
                    'ts': int(ts),
                    'title': title,
                    'annotation': annot,
                    'body': body,
                    'author': author,
                    'url': url,
                }
            return None

        except Exception as e:
            err = e
            retries -= 1
    print(f'Ошибка при извлечении карточки новости: {err}. url: {url}')
    return None
            
def update_cards(urls, cards, last_update, retries=5):
    hrefs = []
    for url in urls:
        new_hrefs = get_fresh_hrefs(url)
        if new_hrefs:
            hrefs.extend(new_hrefs)
    
    for href in hrefs:
        if href not in cards:
            new_card = get_card(href, last_update)
            if new_card:
                cards[href] = new_card
    return cards

def print_card(item):
    print('Время публикации:', datetime.fromtimestamp(item['ts']).isoformat())
    print('Название:', item['title'])
    print('Аннотация:', item['annotation'])
    print('Автор:', item['author'])
    print()

def run_script(duration_hours):
    iteration = 1
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=duration_hours)
    print(f'Время запуска скрипта: {start_time}.')
    print(f'Длительность выполнения: {duration_hours} часа.')
    print(f'Ожидаемое время окончания: {end_time}.')
    print()
    last_upd = start_time.timestamp()
    
    cards = dict()
    
    # буду брать новости про Путина и Байдена, так как встречаются чаще
    urls = ['https://ria.ru/person_Vladimir_Putin/', 'https://ria.ru/person_Dzhozef_Bajjden/']
    
    while datetime.now() < end_time:
        print(f'Итерация {iteration} началась. Последнее обновление: {datetime.fromtimestamp(last_upd).isoformat()}')
        print(f'Текущее время {datetime.now()}')
        cards = update_cards(urls, cards, last_update=last_upd)
        print('Свежие новости:')
        print()
        ts_s = []
        for key in list(cards.keys())[::-1]:
            if cards[key]['ts'] > last_upd:
                print_card(cards[key])
                ts_s.append(cards[key]['ts'])

        iteration += 1
        if ts_s:
            last_upd = max(ts_s)
        else:
            print('<Пусто>')
            print()
        time.sleep(600)

    print(f'Заключительная итерация. Последнее обновление: {datetime.fromtimestamp(last_upd).isoformat()}')
    print(f'Здесь собраны все новости до {end_time} с последнего обновления.')
    print(f'Текущее время {datetime.now()}')
    cards = update_cards(urls, cards, last_update=last_upd)
    print('Свежие новости:')
    print()
    empty_flag = True
    for key in list(cards.keys())[::-1]:
        if cards[key]['ts'] > last_upd and cards[key]['ts'] <= end_time.timestamp():
            print_card(cards[key])
            empty_flag = False
    if empty_flag:
        print('<Пусто>')
        print()
    
    print('Завершение программы...')

run_script(4)