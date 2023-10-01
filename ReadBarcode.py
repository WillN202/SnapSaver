from pyzbar import pyzbar
import cv2

'''
This function decodes the given image and then displays information about the barcode it has read
'''


def decode(image):
    # decodes all barcodes from an image
    try:
        decoded_objects = pyzbar.decode(image)
        for obj in decoded_objects:
            # print barcode type & data
            print("detected barcode:", obj)
            print("Type:", obj.type)
            print("Data:", obj.data)
            ean = obj.data
        print(ean)
        return str(int(ean))


    except Exception as e:
        print('NULL FILE')
        print(e)
        return None


'''
This function takes the files from the directoy and uses cv2 to "read" the image
It then sends this to the decode function to be decoded
Finally it shows the image back to the user
'''


def decodeBarcode(imageFile):
    img = cv2.imread(imageFile)
    img = decode(img)
    return img

# decodeBarcode("./testy3.png")
# print("done")