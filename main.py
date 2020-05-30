from flask import Flask, render_template
#from base64 import b64encode
from surugaya_update import *
app = Flask(__name__)

@app.route("/")
def home():
    df = get_all_data()
    #image = b64encode(obj.image).decode("utf-8")
    del df['image_blob']
    df['url'] = df['url'].map(lambda i: '<a href="' + i + '">' + i + '</a>')
    df['image_url'] = df['image_url'].map(lambda i: '<img src="' + i + '" />')
    pd.set_option('display.max_colwidth', -1)
    df = df.to_html(index=False, escape=False)
    df = df.replace("<<", "&lt;&lt;").replace(">>", "&gt;&gt;")
    return render_template("home.html", data=df)

@app.route("/about")
def about():
    df_items_report = get_all_prices()
    del df_items_report['image_blob']
    df_items_report['url'] = df_items_report['url'].map(lambda i: '<a href="' + i + '">' + i + '</a>')
    df_items_report['image_url'] = df_items_report['image_url'].map(lambda i: '<img src="' + i + '" />')

    pd.set_option('display.max_colwidth', -1)
    df1 = df_items_report[df_items_report['price_check'] == 'Y'].to_html(index=False, escape=False)
    df2 = df_items_report[df_items_report['in_stock'] == 'Y'].to_html(index=False, escape=False)
    df1 = df1.replace("<<", "&lt;&lt;").replace(">>", "&gt;&gt;")
    df2 = df2.replace("<<", "&lt;&lt;").replace(">>", "&gt;&gt;")
    return render_template("about.html", price_change=df1, in_stock=df2)


if __name__ == "__main__":
    app.run(debug=True)

