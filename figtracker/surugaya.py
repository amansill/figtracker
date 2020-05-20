import pandas as pd
import sqlalchemy as sa
import requests
from bs4 import BeautifulSoup
import re
from IPython.core.display import clear_output
import urllib.request, urllib.error

db_name = r'D://websites_db.sqlite'
counter = None

def get_single_item(url, total=1, item_type='all'):
    global counter
    price, title, img, img_blob = ['' for i in range(0,4)]
    if 'suruga-ya' in url:
        page = requests.get(url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')

            divs = soup.find_all(class_="text-red text-bold mgnL10 ")
            if len(divs) > 0:
                match = re.search(r'(\d+\,?\d+)', divs[0].get_text())
                if match:
                    price = match.group().replace(",", "")
            price = int(price or 0)

            divs = soup.find(id="zoom1")
            if divs is not None:
                img = divs['href']
                img_blob = urllib.request.urlopen(img).read()

            divs = soup.find(id="item_title")
            if divs is not None:
                title = divs.get_text().split("<BR>")[0]
                title = title.replace("&lt;&lt;", "<<").replace("&gt;&gt;", ">>").replace('\n','').strip()

    suru_item = {'current_price': price, 'image_url': img, 'image_blob': img_blob, 'title': title}
    counter = counter + 1
    print('Retrieving Suru {} data {} / {}...'.format(item_type,counter,total))
    clear_output(wait=True)
    if item_type == 'all':
        return suru_item
    else:
        return suru_item[item_type]


def get_all_prices():
    global counter

    con = sa.create_engine(r'sqlite:///{}'.format(db_name)).connect()
    df_items = pd.read_sql("select * from surugaya", con)
    total = df_items.shape[0]
    counter = 0

    if total > 0:
        df_items['current_price_new'] = df_items['url'].map(lambda x: get_single_item(x, total=total, item_type='current_price'))
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
        df_items.set_index('url', inplace=True)
        df_items.to_sql('surugaya', con, if_exists='replace')
    else:
        df_items_report = pd.DataFrame()
    con.close()
    return df_items_report


def update_blobs():
    global counter
    con = sa.create_engine(r'sqlite:///{}'.format(db_name)).connect()
    df_items = pd.read_sql("select * from surugaya", con)
    total = df_items.shape[0]
    counter = 0

    if total > 0:
        for i in range(0, total):
            df = new_record(df_items.iloc[i]['url'], total=total)
            df_items.at[i,'current_price'] = df.iloc[0]['current_price']
            df_items.at[i,'image_url'] = df.iloc[0]['image_url']
            df_items.at[i,'image_blob'] = df.iloc[0]['image_blob']

        df_items['last_price'] = df_items.apply(lambda x: x['current_price'] if (x['last_price']==0) and (x['current_price']>0) else x['last_price'], axis=1)
        df_items['last_price'] = df_items['last_price'].astype(int)
        df_items['current_price'] = df_items['current_price'].astype(int)
        df_items.set_index('url', inplace=True)
        df_items.to_sql('surugaya', con, if_exists='replace')
    else:
        df_items = pd.DataFrame()

    con.close()
    return df_items


def new_record(url, total=1):
    df_data = get_single_item(url, total=total)
    df_data['last_price'] = df_data['current_price']
    df = pd.DataFrame(columns=['url', 'title', 'image_url', 'image_blob', 'last_price', 'current_price'],
                      data=[[url, df_data['title'],  df_data['image_url'],  df_data['image_blob'],  df_data['last_price'],  df_data['current_price']]])
    df.set_index('url', inplace=True)
    return df


if __name__ == '__main__':
    df_items_report = get_all_prices()
    #df = update_blobs()
    #df_items_report = pd.DataFrame()
    if df_items_report.shape[0] > 0:
        print(df_items_report[df_items_report['price_check']=='Y'])
        print(df_items_report[df_items_report['back_in_stock'] == 'Y'])

    '''
    con = sa.create_engine(r'sqlite:///{}'.format(db_name)).connect()
    df_new = new_record('https://www.suruga-ya.jp/product/detail/608430302')
    df_new.to_sql('surugaya', con, if_exists='append')
    df_new = new_record('https://www.suruga-ya.jp/product/detail/608582737')
    df_new.to_sql('surugaya', con, if_exists='append')
    df_new = new_record('https://www.suruga-ya.jp/product/detail/608406460')
    df_new.to_sql('surugaya', con, if_exists='append')
    df_new = new_record('https://www.suruga-ya.jp/product/detail/602141069')
    df_new.to_sql('surugaya', con, if_exists='append')
    con.close()
    '''


