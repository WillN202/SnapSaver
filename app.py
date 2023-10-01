from flask import Flask, render_template, redirect, url_for, request, abort
from process_user_actions import register_user, process_login, User, change_details
from productslist import get_product
from flask_wtf.csrf import CSRFProtect
from keyring import get_password
from flask_login import current_user, login_user, login_required, LoginManager, logout_user
from db_connect import db_operations
from shoppinglist import show_shoplist, show_shoplist_plain, add_new_shopping_list, delete_shopping_list, \
del_shopping_list_items, process_barcode_list, make_share, show_shared_list, add_to_list
import barcode

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "."
app.config["SECRET_KEY"] = get_password("secret", "secret")

csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/Login"

@login_manager.user_loader
def get_id(email):
	db = db_operations()
	items = db.get_email_name(email, True)
	return User(items[0], items[1], items[2], items[3])

@app.route("/index")
@app.route("/")
def show_index():
	return render_template("index.html")

@app.route("/Sitemap")
@app.route("/sitemap")
def show_sitemap():
	return render_template("sitemap.html")

@app.route("/Search")
@app.route("/search")
def show_search():
	return barcode.process_search()

@app.route("/FAQ")
@app.route("/faq")
def show_FAQ():
	return render_template("FAQ.html")

@app.route("/Login")
@app.route("/login")
def show_login():
	return render_template("Login.html", err=None)

@app.route("/Login", methods=["POST"])
@app.route("/login", methods=["POST"])
def process_login_route():
	return process_login()

@app.route("/Barcode")
@app.route("/barcode")
def show_barcode():
	return barcode.acceptPic()

@app.route("/barcode", methods=["POST"])
@app.route("/Barcode", methods=["POST"])
def process_barcode():
	return barcode.showpic()

@app.route("/Register")
@app.route("/register")
def show_register():
	return render_template("Register.html", err=None)

@app.route("/Register", methods=["POST"])
@app.route("/register", methods=["POST"])
def process_register():
	return register_user()

@app.route("/Profile")
@app.route("/profile")
@login_required
def show_profile():
	return render_template("Profile.html")

@app.route("/Profile", methods=["POST"])
@app.route("/profile", methods=["POST"])
@login_required
def process_change():
	return change_details()

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("show_index"))

@app.route("/Products")
@app.route("/products")
def show_products():
	return render_template("Product Categories.html")

@app.route("/productlist")
def show_productslist():
	return get_product()

@app.route("/addproduct")
@app.route("/Addproduct")
@app.route("/AddProduct")
def show_addproducts():
	return barcode.show_addproducts()

@app.route("/references")
@app.route("/References")
def show_references():
	return render_template("references.html")

@app.route("/shoppinglist/<sl_id>")
@app.route("/Shoppinglist/<sl_id>")
@login_required
def show_shoppinglist(sl_id):
	return show_shoplist(sl_id)

@app.route("/makeshareable", methods=["POST"])
def make_shareable():
	return make_share()

@app.route("/shoppinglist")
@app.route("/Shoppinglist")
def show_shoppinglist_plain():
	return show_shoplist_plain()

@app.route("/shoppinglist/<sl_id>/<share>")
@app.route("/Shoppinglist/<sl_id>/<share>")
def show_shareable(sl_id, share):
	return show_shared_list(sl_id, share)

@app.route("/shoppinglist/<sl_id>/<share>", methods=["POST"])
@app.route("/Shoppinglist/<sl_id>/<share>", methods=["POST"])
def block_editing():
	return abort(400)

@app.route("/shoppinglist/<sl_id>", methods=["POST"])
@app.route("/Shoppinglist/<sl_id>", methods=["POST"])
def process_shoplist(sl_id):
	return "woo"

@app.route("/addtolist", methods=["POST"])
@login_required
def add_list():
	return add_to_list()
@app.route("/addwithapi", methods=["POST"])
def process_new_product():
    return barcode.add_item_api()

@app.route("/delitems", methods=["POST"])
def del_sl_item():
	return del_shopping_list_items()

@app.route("/addshoppinglist", methods=["POST"])
def add_newlist():
	return add_new_shopping_list()

@app.route("/delshoppinglist", methods=["POST"])
def del_list():
	return delete_shopping_list()

@app.route("/barcodelistprocess", methods=["POST"])
def process_list_barc():
	return process_barcode_list()

@app.route("/addwithoutapi", methods=["POST"])
def process_new_product_noapi():
	return barcode.add_item_without_api()

@app.errorhandler(400)
def dealwith_400():
	return render_template("401.html"), 400

@app.errorhandler(401)
@app.errorhandler(403)
def dealwith_auth():
	return render_template("403.html")

if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True)

