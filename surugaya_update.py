import pandas as pd
import sqlalchemy as sa
import requests
from bs4 import BeautifulSoup
import re
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
    price, title = ['', '']
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
                price = re.sub('[^0-9]', '', divs[0].get_text())

            divs = soup.find(id="item_title")
            if divs is not None:
                title = divs.get_text().split("<BR>")[0]
                title = title.replace("&lt;&lt;", "<<").replace("&gt;&gt;", ">>").replace('\n','').strip()

    suru_item = Surugaya(url=url, current_price=int(price or 0), title=title)
    return suru_item


def get_all_data():
    con = sa.create_engine(r'sqlite:///{}'.format(db_name)).connect()
    df_items = pd.read_sql("select * from surugaya", con)
    return df_items


def get_all_prices():
    global counter

    con = sa.create_engine(r'sqlite:///{}'.format(db_name)).connect()
    df_items = pd.read_sql("select * from surugaya", con)
    total = df_items.shape[0]
    counter = 0

    if total > 0:
        df_items['current_price_new'] = df_items['url'].map(lambda x: get_single_item(x, total=total).current_price)
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
    suru_item = get_single_item(url, total=total)
    suru_item.image_blob = suru_item.get_image_blob(suru_item.image_url)
    df = pd.DataFrame(suru_item.as_dict())
    df.set_index('product_code', inplace=True)
    con = sa.create_engine(r'sqlite:///{}'.format(db_name)).connect()
    df.to_sql('surugaya', con, if_exists='append')
    con.close()
    return


def delete_record(str_input):
    r"""Sends an OPTIONS request.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
    con = sa.create_engine(r'sqlite:///{}'.format(db_name)).connect()
    column = 'url' if 'http' in str_input else 'product_code'
    con.execute("delete from surugaya where {} = '{}'".format(column, str_input))
    return


if __name__ == '__main__':
    #df_items_report = get_all_prices()
    df_items_report = pd.DataFrame()
    if df_items_report.shape[0] > 0:
        print(df_items_report[df_items_report['price_check']=='Y'])
        print(df_items_report[df_items_report['back_in_stock'] == 'Y'])

    df = get_all_data()
    del df['image_blob']
    df['url'] = df['url'].map(lambda i: '<a href="' + i + '">' + i + '</a>')
    df['image_url'] = df['image_url'].map(lambda i: '<img src="' + i + '" />')
    pd.set_option('display.max_colwidth', -1)
    df = df.to_html(index=False, escape=False)
    df = df.replace("<<", "&lt;&lt;").replace(">>", "&gt;&gt;")
    print(df)
    # create_record('https://www.suruga-ya.jp/product/detail/608571216')
    # delete_record('https://www.suruga-ya.jp/product/detail/608290335001')




