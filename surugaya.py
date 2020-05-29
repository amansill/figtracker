class Surugaya(object):
    def __init__(self, url='', current_price=0, image_url='', image_blob='', title=''):
        self.url = url
        self.title = title
        self.image_url = image_url
        self.image_blob = image_blob
        self.last_price = current_price
        self.current_price = current_price

    def as_dict(self):
        return {'url': self.url, 'title': self.title, 'image_url': self.image_url, 'self.image_blob': self.image_blob,
                'self.last_price': self.last_price, 'self.current_price': self.current_price}

