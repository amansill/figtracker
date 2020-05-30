import urllib.request

class Surugaya(object):
    def __init__(self, url, **kwargs):
        self.url = url
        self.title = kwargs['title']
        self.last_price = kwargs['current_price']
        self.current_price = kwargs['current_price']
        self.product_code = url[url.rindex("/")+1:]
        self.image_url = self.get_image_url(self.product_code)
        self.image_blob = ''

    def as_dict(self):
        return {'url': self.url, 'title': self.title, 'image_url': self.image_url, 'self.image_blob': self.image_blob,
                'self.last_price': self.last_price, 'self.current_price': self.current_price}

    def get_image_url(self, product_code):
        return 'https://www.suruga-ya.jp/pics/boxart_m/{}m.jpg'.format(product_code.lower())

    def get_image_blob(self, image_url):
        image_blob = urllib.request.urlopen(image_url).read()
        return image_blob

    #< img src = "data:;base64,{{ image }}" / >