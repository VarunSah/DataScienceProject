""" Understanding and cleaning (if necessary) brand names """

# python
import csv
import collections

# custom
import utils

AMAZON_PRODUCTS_FN = "data/amazon_products.csv"
NEWEGG_PRODUCTS_FN = "data/newegg_products.csv"


# HELPING STANDARDIZE SOME BRAND NAMES... came up with these manually via inspection
NEWEGG_BRAND_MAP = {"wd": "western digital",
                    "startech.com": "startech",
                    "creative labs": "creative",
                    "ht | omega": "ht omega",
                    "pc power and cooling": "ocz",
                    "arctic cooling": "arctic",
                    "beats by dr. dre": "beats",
                    "wd content solutions business": "western digital"}
AMAZON_BRAND_MAP = {"kingston technology": "kingston",
                    "mushkin": "mushkin enhanced",
                    "creative labs": "creative",
                    "lenovo ideapad": "lenovo",
                    "pc power & cooling": "ocz",
                    "fantom": "fantom drives",
                    "corsair gaming": "corsair",
                    "silverstone technology": "silverstone"}



def map_amazon_brand(brand):
    if brand in AMAZON_BRAND_MAP:
        return AMAZON_BRAND_MAP[brand]
    else:
        return brand


def map_newegg_brand(brand):
    if brand in NEWEGG_BRAND_MAP:
        return NEWEGG_BRAND_MAP[brand]
    else:
        return brand


def statistics(newegg_products, amazon_products):

    newegg_brand_counter = collections.Counter([item[6].lower() for item in newegg_products])
    amazon_brand_counter = collections.Counter([item[5].lower() for item in amazon_products])

    with open("output/newegg_brands.txt", "w") as f:
        for k, v in sorted(newegg_brand_counter.items(), key=lambda x: x[1]):
            print(k, v, file=f)

    with open("output/amazon_brands.txt", "w") as f:
        for k, v in sorted(amazon_brand_counter.items(), key=lambda x: x[1]):
            print(k, v, file=f)

    print("Unique newegg brands:", len(newegg_brand_counter))
    print("Unique amazon brands:", len(amazon_brand_counter))

    # overlap
    overlapping_brands = newegg_brand_counter.keys() & amazon_brand_counter.keys()
    print(len(overlapping_brands))
    print(overlapping_brands)

    overlapping_items_amazon = 0
    for k, v in amazon_brand_counter.items():
        for brand in overlapping_brands:
            if k == brand:
                overlapping_items_amazon += v
    print(overlapping_items_amazon)

    overlapping_items_newegg = 0
    for k, v in newegg_brand_counter.items():
        for brand in overlapping_brands:
            if k == brand:
                overlapping_items_newegg += v
    print(overlapping_items_newegg)


def main():

    # load newegg products
    newegg_products = utils.load_csv(NEWEGG_PRODUCTS_FN, skip_first=True)
    amazon_products = utils.load_csv(AMAZON_PRODUCTS_FN, skip_first=True)

    statistics(newegg_products, amazon_products)


if __name__ == "__main__":
    main()