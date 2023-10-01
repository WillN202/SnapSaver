import MySQLdb as sqlclient
from keyring import get_password
from werkzeug.security import generate_password_hash, check_password_hash
from random import randint
from uuid import uuid4

class db_operations:
    """Allows DB access, searching, and user/password fetching"""
    __username = "t07913wn"  # Set your own username here

    def __init__(self):
        """Connects to DB and sets up objects for other methods"""

        try:
            self.db = sqlclient.connect(
                host="dbhost.cs.man.ac.uk",
                user=self.__username,
                password=get_password(
                    "database",
                    self.__username), database="2020_comp10120_y11")

            self.cursor = self.db.cursor()

        except BaseException:  # If connection fails
            print("SQL connection failed.")
            raise Exception

    def insert_item(self, ean, name, imglocation, category):
        """Inserts row into item table"""
        try:
            self.cursor.execute(
                "INSERT INTO item VALUES(%s, %s, %s, %s)", [ean, name, imglocation, category])
            self.db.commit()

            return True

        except BaseException:
            print(repr(BaseException))

            return False

    def search_item(self, ean):
        """Returns tuple with ean, name, imglocation of an item, None otherwise"""

        self.cursor.execute("SELECT * FROM item WHERE ean=%s", [ean])
        result = self.cursor.fetchall()
        if len(result) == 0:
            return None
        else:
            return result

    def insert_item_price(self, storeID, ean, price):
        """Inserts row into item_price_at_store field"""

        self.cursor.execute(
            "INSERT INTO itempriceatstore (name, ean, price, votes) VALUES(%s, %s, %s, 0)", [storeID, ean, price])
        self.db.commit()

    def insert_user(self, email, password, name, postcode):
        """Takes email and UNHASHED password and inserts row into user table"""
        try:
            ID = str(uuid4())
            self.cursor.execute(
                "INSERT INTO user VALUES(%s, %s, %s, %s, %s)",
                [ID[0:6],
                email,
                generate_password_hash(password),
                name, postcode])
            self.db.commit()
            return True
        except BaseException:
            return False

    def verify_user(self, email, password):
        """Verifies is a user exists & password is valid, returns true if
        password valid, false if it doesn't"""
        self.cursor.execute(
            "SELECT email, passwordhash from user WHERE email=%s",
            [email])
        results = self.cursor.fetchall()

        if results:
            return check_password_hash(results[0][1], password)
        else:
            print("not found!")
            return False

    def alter_email(self, email, userID):
        self.cursor.execute("UPDATE user SET email=%s WHERE userID=%s", [email, userID])
        self.db.commit()

    def alter_password(self, password, userID):
        self.cursor.execute("UPDATE user SET passwordhash=%s WHERE userID=%s", [generate_password_hash(password), userID])
        self.db.commit()

    def alter_name(self, name, userID):
        self.cursor.execute("UPDATE user SET name=%s WHERE userID=%s", [name, userID])
        self.db.commit()

    def alter_postcode(self, postcode, userID):
        self.cursor.execute("UPDATE user SET postcode=%s WHERE userID=%s", [postcode, userID])
        self.db.commit()

    def get_shopping_list_info(self, userID, name):
        """Return Shop and Shareable from shopping list"""
        self.cursor.execute("SELECT shop, shareable FROM shopping_list WHERE userID=%s AND name=%s", [userID, name])
        result = self.cursor.fetchall()
        return result[0]

    def delete_shopping_list(self, UserID, name):
        """Deletes shopping list from DB"""
        self.cursor.execute("DELETE FROM shopping_list WHERE userID=%s AND name=%s", [UserID, name])
        self.cursor.execute("DELETE FROM shopping_list_items WHERE userID=%s AND name=%s", [UserID, name])
        self.db.commit()

    def change_shareable(self, userID, name, is_shareable):
        """Changes if an item is shareable or not and gives shareableID"""
        if is_shareable:
            self.cursor.execute("UPDATE shopping_list SET shareable=%s WHERE userID=%s AND name=%s", [randint(0, 1000), userID, name])
        else:
            self.cursor.execute("UPDATE shopping_list SET shareable=0 WHERE userID=%s AND name=%s", [userID, name])
        
        self.db.commit()

    def check_item_in_list(self, userID, name, ean):

        """If item is in list returns true, otherwise returns false"""
        self.cursor.execute("SELECT name FROM shopping_list_items WHERE userID=%s AND name=%s AND ean=%s", [userID, name, ean])
        result = self.cursor.fetchall()
        if result:
            return True
        else:
            return False
    
    def mark_checked_item_in_list(self, userID, name, ean):
        """Marks an item as checked in the DB"""
        self.cursor.execute("UPDATE shopping_list_items SET checked=1 WHERE userID=%s AND name=%s AND ean=%s", [userID, name, ean])
        self.db.commit()

    def get_id_shared_list(self, name, shareID):
        """Returns the userID of the user who created a list that was shared"""
        self.cursor.execute("SELECT userID FROM shopping_list WHERE name=%s AND shareable=%s", [name, shareID])
        results = self.cursor.fetchall()
        if results == ():
            return None
        else:
            return results[0]

    def del_shopping_list_item(self, UserID, name, ean):
        """Deletes an item from the shopping list"""
        self.cursor.execute("DELETE FROM shopping_list_items WHERE userID=%s AND name=%s AND ean=%s", [UserID, name, ean])
        self.db.commit()

    def insert_shopping_list(self, name, userID, shop):
        """Creates a shopping list which can hold items"""
        try:
            self.cursor.execute(
                "INSERT INTO shopping_list VALUES(%s, %s, %s, %s)", [name, userID, shop, 0])
            self.db.commit()
            return True
        except BaseException:
            return False

    def insert_shopping_list_item(self, name, userID, ean, quantity):
        """Inserts an item into a shopping list, must have foreign key
        relation in insert_shopping_list """

        self.cursor.execute(
            "INSERT INTO shopping_list VALUES(%s, %s, %s, %s)",
            [name,
             userID,
             ean,
             quantity])

        self.db.commit()

    def get_postcode(self, userID):
        """Gets the postcode of the associated user"""
        self.cursor.execute("SELECT postcode FROM user WHERE userID=%s", [userID])

        results = self.cursor.fetchall()
        
        return results[0][0]
    def get_shopping_list_items(self, userID, name):
        """Returns ean and quantity of items in a shopping list"""
        self.cursor.execute("SELECT ean, quantity, checked FROM shopping_list_items WHERE name=%s AND userID=%s", [name, userID])
        return self.cursor.fetchall()

    def get_stores(self):
        """Returns a list of all the stores in the system with their name and postcode"""

        self.cursor.execute("SELECT name, postcode FROM store")
        return self.cursor.fetchall()

    def get_item_at_store(self, ean):
        """Returns a list of all stores where a price is recorded for an item 
        with that ean"""

        self.cursor.execute("SELECT DISTINCT store.name, postcode FROM store, itempriceatstore WHERE ean=%s AND store.name = itempriceatstore.name", [ean])
        result = self.cursor.fetchall()
        if len(result) == 0:
            return None
        else:
            return result

    def get_item_price_at_store(self, store, ean):
        """Returns price of an item when given store name and ean of product, if it exists"""
        self.cursor.execute("SELECT price, votes FROM itempriceatstore WHERE name=%s and ean=%s", [store, ean])
        
        price = self.cursor.fetchall()
        if len(price) == 0:
            return None
        elif len(price) == 1:
            return float(price[0][0])
        else:
            price = price[0][0]
            score = (int(price[0][1]) + 3)** 0.85
            for item in price:
                tscore = (int(item[1]) + 3)** 0.85
                if tscore > score:
                    score = tscore
                    price = item[0]

            return price



    def get_email_name(self, index, Usrid=False):
        """Returns list of email and passhash given userID"""
        if Usrid:
            self.cursor.execute("SELECT email, name, postcode, userID FROM user WHERE userID=%s", [index])
        else:
            self.cursor.execute("SELECT email, name, postcode, userID FROM user WHERE email=%s", [index])
        results = self.cursor.fetchall()
        print(results)
        results = results[0]

        return [results[0], results[1], results[2], results[3]]

    def get_shopping_lists(self, userID):
        """Returns shopping lists name from a particular userID"""

        self.cursor.execute("SELECT name FROM shopping_list WHERE userID=%s", [userID])
        return self.cursor.fetchall()

    def search_category(self, category):
        """Searches items table returns items in the specified category,returns name
         and imglocation of each item or None"""

        self.cursor.execute("SELECT name, imglocation, ean FROM item WHERE category=%s", [category])
        results = self.cursor.fetchall()
        return results

    def search_byname_cat(self, term, category=""):
        """Searches items table by provided search term and optionally the category, returns ean, name and imglocation"""
        if category == "":
            self.cursor.execute("SELECT ean, name, imglocation FROM item WHERE name LIKE %s", ["%" + term + "%"])
        elif term == "":
            self.cursor.execute("SELECT ean, name, imglocation FROM item WHERE category=%s", [category])

        else:
            self.cursor.execute("SELECT ean, name, imglocation FROM item WHERE name LIKE %s AND category=%s", ["%"+term+"%", category])

        results = self.cursor.fetchall()
        if results == ():
            return None
        else:
            return results

    def get_average_price_store(self, ean, store):
        """Returns average price for an item over all the type of stores in the DB"""
        
        self.cursor.execute("SELECT avg(price) from itempriceatstore WHERE votes > 2 AND ean=%s AND name LIKE %s", [ean, "%"+store+"%"])
        results = self.cursor.fetchall()
        return results[0][0]

    def __del__(self):
        """Called when object is destroyed, closes DB connection"""

        try:
            self.db.close()

        except BaseException:
            pass

    def close(self):
        """Closes the DB connection manually"""
        self.__del__()
