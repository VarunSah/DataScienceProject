""" Cleans the Amazon product table which was generated from the scraped data. """

# python
import csv
import re
import collections

# custom
import utils
import brands

CATEGORY_MAP_FN = "data/category_map.csv"
DATA_FN = "data/amazon_products_new.csv"
OUT_FN = "data/amazon_products_clean.csv"


def main():

    category_map = utils.load_category_map(CATEGORY_MAP_FN)

    header = ["ASIN", "NAME", "CATEGORY", "PRICE", "NUM_REVIEWS", "BRAND", "INFO"]

    amazon_products = utils.load_csv(DATA_FN, skip_first=True)

    # check for duplicate asins
    counter = collections.Counter([x[0] for x in amazon_products])
    duplicates = {}
    for k, v in counter.items():
        if v > 1:
            duplicates[k] = 0
            # print(k)

    with open(OUT_FN, "w") as f_out:

        writer = csv.writer(f_out, delimiter=",")
        writer.writerow(header)

        for product in amazon_products:

            # note the amazon csv is in a different order than the output is going to be
            asin, name, brand, category, price, num_reviews, info = product

            # if there's a duplicate asin, make sure we only process it once
            if asin in duplicates:
                if duplicates[asin] == 1:
                    continue
                else:
                    duplicates[asin] = 1

            # replace category number with standardized category string
            try:
                category = category_map[category]
            except KeyError as e:
                print("Encountered an unexpected category: {}".format(category))
                quit()

            # remove the dollar sign and spaces from the price
            price = re.sub("[^0-9.]", "", price)

            # confirm price is in the correct format
            pattern = re.compile("\d+\.\d\d|^$")
            if not pattern.match(price):
                print("Unable to format price correctly: {}".format(price))
                quit()

            # remove excess white space from the brand name and name
            brand = brand.strip()
            name = name.strip()

            # make name lowercase
            name = name.lower()

            # replace parenthesis, slashes, dashes, brackets
            name = re.sub("\(|\)|\\|/|\[|\]|:|;|\||,", " ", name)

            # remove "None" from the brand name - we will just leave those as missing values for now.
            brand = brand.replace("None", "")

            # make brand lowercase
            brand = brand.lower()

            # apply brand name map
            brand = brands.map_amazon_brand(brand)

            if info == "None None None":
                info = ""
            info = info.lower()
            info = re.sub("\(|\)|\\|/|\[|\]|:|;|\||,", " ", info)

            # if the name is missing, get rid of this record. It will be really hard to match, and what kind
            # of product doesn't have a name anyway?
            if name == "":
                continue


            writer.writerow([asin, name, category, price, num_reviews, brand, info])


if __name__ == "__main__":
    main()