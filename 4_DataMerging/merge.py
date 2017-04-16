""" combines data into a single set """

import utils
import csv

# filename constants
AMAZON_PRODUCTS_FN = "data/amazon_products.csv"
NEWEGG_PRODUCTS_FN = "data/newegg_products.csv"
MATCHES_FN = "data/matched_tuples.csv"
OUTPUT_FN = "output/combined_products.csv"


def product_dictionary(products):
    """ creates a product dictionary key'd on the first item """

    product_dict = {}
    for product in products:
        product_dict[product[0]] = product

    return product_dict


def combine_name(amazon_name, newegg_name):
    """ combines the names """

    # select the shorter and longer names
    if len(amazon_name) >= len(newegg_name):
        longer = amazon_name
        shorter = newegg_name
    else:
        longer = newegg_name
        shorter = amazon_name

    # split each name into tokens
    longer_tokens = longer.split()
    shorter_tokens = shorter.split()

    # check which parts of the shorter name need to be appended to the longer name
    need_appending = []
    for shorter_token in shorter_tokens:
        if shorter_token not in longer_tokens:
            need_appending.append(shorter_token)

    if need_appending:
        # append the shorter tokens to the longer name
        longer += " |"
        for token in need_appending:
            longer += " {}".format(token)

    return longer


def combine_price(amazon_price, newegg_price):
    """ combines the prices """

    # cases where one or both of the prices is missing
    if amazon_price == "":
        return newegg_price
    elif newegg_price == "":
        return amazon_price
    else:
        newegg_price = float(newegg_price)
        amazon_price = float(amazon_price)
        avg = round((newegg_price + amazon_price) / 2, 2)

        # output expecting a string
        avg = str(avg)
        return avg


def combine_products(amazon_product_dict, newegg_product_dict, matches):
    """ combines all the matching newegg and amazon tuples """

    combined_products = []

    # loop through match and create a new row for the combined table
    for asin, nid in matches:

        # place each of the output data in its own variable for readability
        rid = newegg_product_dict[nid][1]
        name = combine_name(amazon_product_dict[asin][1], newegg_product_dict[nid][2])
        price = combine_price(amazon_product_dict[asin][3], newegg_product_dict[nid][4])
        category = amazon_product_dict[asin][2]
        brand = amazon_product_dict[asin][5]
        amazon_info = amazon_product_dict[asin][6]
        newegg_info = newegg_product_dict[nid][7]
        amazon_num_reviews = amazon_product_dict[asin][4]
        newegg_num_reviews = newegg_product_dict[nid][5]

        # put into a vector along with asin and nid
        combined_product = [asin, nid, rid, name, price, category, brand, amazon_info,
                            newegg_info, amazon_num_reviews, newegg_num_reviews]

        # add to list
        combined_products.append(combined_product)

    return combined_products


def main():

    # amazon header (for reference)
    # ASIN, NAME, CATEGORY, PRICE, NUM_REVIEWS, BRAND, INFO

    # newegg header (for reference)
    # NID, RID, NAME, CATEGORY, PRICE, NUM_REVIEWS, BRAND, INFO

    # load amazon products
    amazon_products = utils.load_csv(AMAZON_PRODUCTS_FN, skip_first=True)
    amazon_product_dict = product_dictionary(amazon_products)

    # load newegg products
    newegg_products = utils.load_csv(NEWEGG_PRODUCTS_FN, skip_first=True)
    newegg_product_dict = product_dictionary(newegg_products)

    # load matches
    matches = utils.load_csv(MATCHES_FN, skip_first=True)

    # combine the products
    combined_products = combine_products(amazon_product_dict, newegg_product_dict, matches)

    # output schema header
    header = ["ASIN", "NID", "RID", "NAME", "PRICE", "CATEGORY", "BRAND",
              "AMAZON_INFO", "NEWEGG_INFO", "AMAZON_NUM_REVIEWS", "NEWEGG_NUM_REVIEWS"]

    # save to a csv file
    with open(OUTPUT_FN, "w") as out_f:
        writer = csv.writer(out_f, delimiter=",")
        # write the header row
        writer.writerow(header)
        # write the products
        for product in combined_products:
            writer.writerow(product)


if __name__ == "__main__":
    main()