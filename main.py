from flask import Flask, render_template

app = Flask(__name__)

#df_items_report = get_all_prices()
#if df_items_report.shape[0] > 0:
#    print(df_items_report[df_items_report['price_check']=='Y'])
#    print(df_items_report[df_items_report['back_in_stock'] == 'Y'])
# df_items_report.to_html()

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)