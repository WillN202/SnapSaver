import os

from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug.utils import secure_filename

from api_access import api_accesser
from db_connect import db_operations
from ReadBarcode import decodeBarcode
from babel.numbers import format_currency
from uuid import uuid4
from flask_login import current_user

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "."
app.config["TEMP_UPLOAD_FOLDER"] = "tmp"
app.config["ITEM_IMG_UPLOAD_FOLDER"] = "static/item_pics"

@app.route("/Barcode")
def acceptPic():
    print("ran")
    return render_template("Barcodes2.html", error=0)

@app.route("/Barcode", methods=["POST"])
def showpic():
    
    if 'image' in request.files:
        
        img = request.files["image"]
        if not(img.filename == ''):
            print("next")

            print("valid filename")
            path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(img.filename))
            img.save(path)
            strb = decodeBarcode(path)
            os.remove(path)

            if strb is None:
                return render_template("Barcode.html", error=3)

        elif request.form["bartext"] != "":
            print("text")
            strb = request.form["bartext"]
        else:
            return render_template("Barcode.html", error=1)
    else:
        return render_template("Barcode.html", error=1)
    
    print(strb)

    

    db = db_operations()
    item = db.search_item(strb)
    print(item, "got here")

    if item is None:
        # return render_template("Barcode.html", error=2)
        api_result = api_accesser.pull_product(strb, False)
        print(api_result)
        if api_result is None:
            return redirect(url_for("show_addproducts", ean=strb))
        else:
            return redirect(url_for("show_addproducts", ean=strb, name=api_result[0], imglocation=api_result[1]))


    item = item[0]
    stores_list = db.get_item_at_store(strb)
    postcode = current_user.postcode

    sorted_stores = api_accesser.get_distance(stores_list=stores_list, postcode=postcode)
    sorted_stores = sorted(sorted_stores, key=lambda k: k['distance']) 
    

    stores_prices_list = []
    no_stores = 3
    if len(sorted_stores) < 3:
        no_stores = len(sorted_stores)

    for i in range(0, no_stores):
        stores_prices_list.append({"name": sorted_stores[i]["name"], "price": str(format_currency(db.get_item_price_at_store(sorted_stores[i]["name"], strb), "GBP")), "link":api_accesser.get_maps_url(sorted_stores[i]["name"], origin=postcode)})
    print("final")
    print(stores_prices_list)

    img_loc = item[2]
    if img_loc[0:4] != "http":
        img_loc = "item_pics/" + item[2]

    shopping_lists = db.get_shopping_lists(current_user.id)
    return render_template("ProductPageSingle.html", product=item[1], img=img_loc, store_prices=stores_prices_list, no_item=no_stores, ean=strb, shopping_lists=shopping_lists)
    


@app.route("/addproduct")
@app.route("/Addproduct")
@app.route("/AddProduct")
def show_addproducts():

    if len(list(request.args.keys())) > 1:
        products = [request.args["name"], request.args["imglocation"]]
    else:
        products = ["", ""]
    db = db_operations()
    stores_list = db.get_stores()
    return render_template("add_product.html", product_info=products, stores_list=stores_list, ean=request.args["ean"])

def add_item_api():
    name = request.form["name"]
    imglocation = request.form["image"]
    category = request.form["category"]
    price = request.form["price"]
    ean = request.form["ean"]
    store = request.form["store"]

    
    if category == "" or store == "":
        abort(401)

    db = db_operations()
    db.insert_item(ean, name, imglocation, category)
    db.insert_item_price(store, ean, price)

    return redirect(url_for("show_barcode"))

def add_item_without_api():
    ean = request.form["ean"]
    category = request.form["category"]
    price = request.form["price"]
    store = request.form["store"]
    name = request.form["name"]

    if category == "" or store == "":
        abort(401)

    if 'image' in request.files:
        img = request.files["image"]
        if img.filename == "":
            return redirect(url_for("show_barcode"))

        path = os.path.join(app.config['TEMP_UPLOAD_FOLDER'], secure_filename(img.filename))
        img.save(path)

        extension = os.path.splitext(path)[1]
        if not (extension in [".jpg", ".jpeg", ".gif", ".png", ".jfif", ".svg"]):
            abort(401)

        filename = str(uuid4())
        filename = filename[0:5] + extension
        imglocation = filename

        filename = os.path.join(app.config["ITEM_IMG_UPLOAD_FOLDER"], filename)
        os.replace(path, filename)

        db = db_operations()
        db.insert_item(ean, name, imglocation, category)
        db.insert_item_price(store, ean, price)

    return redirect(url_for("show_barcode"))

def process_search():
    args = list(request.args.keys())
    term = ""
    category = ""
    if len(list(args)) < 1:
        return render_template("Search.html", products=[], err=None)

    if not("term" in args) and not("category" in args):
        return render_template("search.html", products=[], err="Enter a value for category or search")
    if "term" in args:
        term = request.args["term"]
    
    if "category" in args:
        category = request.args["category"]

    db = db_operations()
    matched_products = db.search_byname_cat(term, category)

    supermarkets = ["Aldi", "Lidl", "Tesco", "Morrison", "Asda", "Sainsbury"]
    products = []

    for item in matched_products:
        img_loc = item[2]
        if img_loc[0:4] != "http":
            img_loc = "item_pics/" + img_loc
        
        item_dict = {"name": item[1], "imglocation":img_loc}
        
        for store in supermarkets:
            print(item[0], " ", store)
            avg_price = db.get_average_price_store(item[0], store)
            if avg_price is not None:
                avg_price = format_currency(avg_price, "GBP")

            item_dict.update({store: avg_price})
        
        products.append(item_dict)

    print(products)
    return render_template("Search.html", products=products, err=None)


    



        
        


        

