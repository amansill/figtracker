import pandas as pd
import sqlalchemy as sa
import requests
from bs4 import BeautifulSoup
import re
from IPython.core.display import clear_output
import urllib.request, urllib.error
import time
from surugaya import Surugaya

db_name = r'D://websites_db.sqlite'
counter = 0
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=100,
    pool_maxsize=100, max_retries=20)
session.mount('http://', adapter)


def get_single_item(url, total=1, item_type='all'):
    global counter
    price, title, img, img_blob = ['' for i in range(0,4)]
    if 'suruga-ya' in url:
        counter = counter + 1
        while True:
            try:
                page = session.get(url, timeout=15)
                time.sleep(2)
            except Exception as e:
                print(e)
                time.sleep(5)
                continue
            break
        if page.status_code == 200:
            print('Retrieving Suru {} data {} / {}...'.format(item_type, counter, total))
            soup = BeautifulSoup(page.content, 'html.parser')

            divs = soup.find_all(class_="text-red text-bold mgnL10 ")
            if len(divs) > 0:
                match = re.search(r'(\d+\,?\d+)', divs[0].get_text())
                if match:
                    price = match.group().replace(",", "")

            divs = soup.find(id="zoom1")
            if divs is not None:
                img = divs['href']
                img_blob = urllib.request.urlopen(img).read()

            divs = soup.find(id="item_title")
            if divs is not None:
                title = divs.get_text().split("<BR>")[0]
                title = title.replace("&lt;&lt;", "<<").replace("&gt;&gt;", ">>").replace('\n','').strip()

    suru_item = {'current_price': int(price or 0), 'image_url': img, 'image_blob': img_blob, 'title': title}
    # suru_item = Surugaya(url=url, current_price=int(price or 0), image_url=img, image_blob=img_blob, title=title)
    clear_output(wait=True)
    if item_type == 'all':
        return suru_item
    else:
        return suru_item[item_type]
    # return suru_item


def get_all_prices():
    global counter

    con = sa.create_engine(r'sqlite:///{}'.format(db_name)).connect()
    df_items = pd.read_sql("select * from surugaya", con)
    total = df_items.shape[0]
    counter = 0

    if total > 0:
        df_items['current_price_new'] = df_items['url'].map(lambda x: get_single_item(x, total=total, item_type='current_price'))
        # df_items['current_price_new'] = df_items['url'].map(lambda x: get_single_item(x, total=total).current_price)
        df_items['last_price'] = df_items.apply(lambda x: x['current_price'] if (x['last_price']==0) and (x['current_price']>0) else x['last_price'], axis=1)
        df_items['last_price'] = df_items['last_price'].astype(int)
        df_items['current_price'] = df_items['current_price'].astype(int)

        df_items_report = df_items.copy()
        df_items_report['price_check'] = df_items_report.apply(lambda x: 'Y' if (x['current_price_new'] < x['last_price']) and (x['current_price_new'] > 0) else '', axis=1)
        df_items_report['back_in_stock'] = df_items_report.apply(lambda x: 'Y' if (x['current_price'] == 0) and (x['current_price_new'] > 0) else '', axis=1)

        df_items['current_price'] = df_items['current_price_new']
        del df_items['current_price_new']
        df_items_report['current_price'] = df_items_report['current_price_new']
        del df_items_report['current_price_new']
        del df_items_report['image_blob']
        df_items.set_index('url', inplace=True)
        df_items.to_sql('surugaya', con, if_exists='replace')
    else:
        df_items_report = pd.DataFrame()
    con.close()
    return df_items_report


def create_record(url, total=1):
    df_data = get_single_item(url, total=total)
    # df = pd.DataFrame(suru.as_dict())
    df = pd.DataFrame(columns=['url', 'title', 'image_url', 'image_blob', 'last_price', 'current_price'],
                      data=[[url, df_data['title'],  df_data['image_url'],  df_data['image_blob'],  df_data['last_price'],  df_data['current_price']]])
    df.set_index('url', inplace=True)
    df['last_price'] = df['current_price']
    con = sa.create_engine(r'sqlite:///{}'.format(db_name)).connect()
    df.to_sql('surugaya', con, if_exists='append')
    con.close()
    return


def delete_record(url):
    con = sa.create_engine(r'sqlite:///{}'.format(db_name)).connect()
    con.execute("delete from surugaya where url = {}".format(url))
    return


if __name__ == '__main__':
    #df_items_report = get_all_prices()
    #df = update_blobs()
    df_items_report = pd.DataFrame()
    if df_items_report.shape[0] > 0:
        print(df_items_report[df_items_report['price_check']=='Y'])
        print(df_items_report[df_items_report['back_in_stock'] == 'Y'])

    create_record('https://www.suruga-ya.jp/product/detail/601803010')




