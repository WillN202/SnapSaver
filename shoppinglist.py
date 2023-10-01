from flask import Flask, render_template, redirect, request, url_for, abort
from flask_login import current_user
from db_connect import db_operations
from babel.numbers import format_currency
from barcode import decodeBarcode
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "."

def get_setup_info():
    db = db_operations()
    shopping_lists = db.get_shopping_lists(current_user.id)
    stores_list = db.get_stores()
    return [shopping_lists, stores_list]


def show_shoplist_plain():
    if len(list(request.args.keys())) > 0:
        return redirect(url_for("show_shoppinglist", sl_id=request.args["shoppingList"]))

    lists_stores = get_setup_info()
    return render_template("shoppinglist.html", list=lists_stores[0], store_list=lists_stores[1], list_info=[""]*7, list_items=[], selected_list=False, list_name="", err=None)


def show_shoplist(sl_id, uid=""):
    if len(list(request.args.keys())) > 0:
        return redirect(url_for("show_shoppinglist", sl_id=request.args["shoppingList"]))

    if uid == "":
        uid = current_user.id

    all_prices_got = True
    lists_stores = get_setup_info()
    db = db_operations()

    result = db.get_shopping_list_info(current_user.id, sl_id)
    list_info = [current_user.name, result[0], "", "", sl_id, result[1]]
    result = db.get_shopping_list_items(current_user.id, sl_id)
    list_items = []
    total = 0
    checked_total = 0

    for item in result:
        name = db.search_item(item[0])
        price = db.get_item_price_at_store(list_info[1], item[0])
        if not price:
            price = "£ ---"
            all_prices_got = False
        else:
            total += float(price) * item[1]
            if item[2]:
                checked_total += float(price) * item[1]
        list_items.append([name[0][1], format_currency(price, "GBP"), str(item[1]), item[2], item[0]])

        if all_prices_got:
            list_info[2] = format_currency(total, "GBP")
            list_info[3] = format_currency(checked_total, "GBP")
            
    return render_template("shoppinglist.html", list=lists_stores[0], store_list=lists_stores[1], list_info=list_info,
            list_items=list_items, selected_list=True, list_name=sl_id, err=None)

def add_new_shopping_list():
    db = db_operations()
    name = request.form["listname"]
    store = request.form["store"]
    userID = current_user.id

    print("name", name)
    print("store", store)

    if name == "" or store == "":
        print("broke")
        return abort(400)

    db = db_operations()
    success = db.insert_shopping_list(name, userID, store)
    if success:
        return redirect(url_for("show_shoppinglist", sl_id=name))
    else:
        return redirect(url_for("show_shoppinglist_plain"))

def delete_shopping_list():
    if request.form["name"] == "":
        return abort(400)

    db = db_operations()
    print("name", request.form["name"])
    db.delete_shopping_list(current_user.id, request.form["name"])
    return redirect(url_for("show_shoppinglist_plain"))

def del_shopping_list_items():
    print(request.form.getlist("item1"))
    items_removed = request.form.getlist("item1")
    # print(request.form[a[0]+"ean"])
    db = db_operations()
    for item in items_removed:
        ean = request.form[item + "ean"]
        db.del_shopping_list_item(current_user.id, request.form["name"], ean)

    return redirect(url_for("show_shoppinglist", sl_id=request.form["name"]))

def process_barcode_list():
    if 'image' in request.files:
        img = request.files["image"]
        if not(img.filename == ''):
          
            path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(img.filename))
            img.save(path)
            strb = decodeBarcode(path)
            os.remove(path)

            if strb is None:
                return "whoops"
    else:
        return "whoops!"

    db = db_operations()
    if db.check_item_in_list(current_user.id, request.form["list_name"], strb):
        db.mark_checked_item_in_list(current_user.id, request.form["list_name"], strb)
    else:
        db.insert_shopping_list_item(request.form["list_name"], current_user.id, strb, 1)

    return redirect(url_for("show_shoppinglist", sl_id=request.form["list_name"]))

def make_share():
    db = db_operations()
    if "share" in request.form:
        db.change_shareable(current_user.id, request.form["list_name"], True)
    else:
        db.change_shareable(current_user.id, request.form["list_name"], False)

    return redirect(url_for("show_shoppinglist", sl_id=request.form["list_name"]))   

def show_shared_list(sl_id, shareID):
    db = db_operations()
    user = db.get_id_shared_list(sl_id, shareID)
    if user:
        return show_shoplist(sl_id, user)
    else:
        return abort(400)

def add_to_list():
    db = db_operations()
    db.insert_shopping_list_item(request.form["category"], current_user.id, request.form["ean"], 1)
    return redirect(url_for("show_shoppinglist", sl_id=request.form["category"]))