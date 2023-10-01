from flask import Flask, render_template, redirect, url_for, request 
from db_connect import db_operations
from babel.numbers import format_currency
app = Flask(__name__)


def get_product():
    db = db_operations()
    if len(request.args) != 1:
        return redirect(url_for("show_products"))

    db = db_operations()
    products = db.search_category(request.args["category"])
    formatted_products = []
    supermarkets = ["Aldi", "Lidl", "Tesco", "Morrison", "Asda", "Sainsbury"]
    for item in products:
        dicttmp = {"name": item[0], "imglocation": item[1]}
        for store in supermarkets:
            tmp = db.get_average_price_store(item[2], store)
            if tmp != None:
                dicttmp.update({store: format_currency(tmp, "GBP")})
            else:
                dicttmp.update({store: "None"})
        formatted_products.append(dicttmp)


    return render_template("product_page.html", product_list=formatted_products)
