from requests import get
from keyring import get_password
from db_connect import db_operations
from re import sub

class api_accesser:
    """Allows products to be pulled from the BarcodeFinder API and Google Distance API"""

    @classmethod
    def pull_product(cls, ean, add_to_db):
        """Pings API for product, returns name, brand and img location in a tuple if available.
        None otherwise. Takes ean as string, add_to_db Boolean"""

        try:
            response = get(
                "https://api.barcodelookup.com/v2/products", params={
                    "barcode": ean, "key": get_password(
                        "api", "t07913wn")}, headers={"Content-Type": "application/json"}, timeout=2)

            if response.status_code != 200:
                return None

            content = response.json()
        except BaseException:
            return None

        # if add_to_db:

        #     db_op = db_operations()
        #     db_op.insert_item(ean,
        #                       content["products"][0]["product_name"],
        #                       content["products"][0]["images"][0])
        #     db_op.close()
        return (content["products"][0]["product_name"],
                content["products"][0]["images"][0])

    @classmethod
    def get_distance(cls, stores_list, userID="", postcode=""):
        """Gets distance between user, judging by saved postcode or given location, and stores"""
        print(stores_list)
        db = db_operations()
        if postcode == "":
            if userID == "":
                return None
            
            postcode = db.get_postcode(userID)
            db = None

        stores = ""
        for item in stores_list:
            stores += sub(" ", "+", item[0]) + "+" + sub(" ", "+", item[1]) + "|"

        response = get("https://maps.googleapis.com/maps/api/distancematrix/json", params={"units": "imperial", "origins": postcode,
             "destinations": stores, 
             "mode":"walking", "key":get_password("googleapi", "googleapi")})

        content = response.json()
        print(content)
        content = content["rows"][0]["elements"]
        print(content[0]["distance"]["value"])

        stores_distances = []
        
        for i in range(0, len(stores_list)):
            if content[i]["status"] != "OK":
                continue

            stores_distances.append({"name": stores_list[i][0], "distance": content[i]["distance"]["value"]})
        return stores_distances
    
    @classmethod
    def get_maps_url(self, destination, origin="", userID=""):
        """Gets Maps Url showing route guidance for destination store and 
        origin provided or got from user"""

        if origin == "":
            if userID == "":
                return None
            
            origin = db.get_postcode(userID)
            db = None

        url = "https://www.google.com/maps/dir/?api=1&"
        url += "origin=" + origin + "&"
        url += "destination=" + sub(" ", "", destination) + "&"

        return url + "travelmode=transit"


