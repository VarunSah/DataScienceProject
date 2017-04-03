""" Organizes the scraped newegg data into the standard schema """

# python
import csv
import os
from os.path import join
import re

# custom
import utils
import brands

DATA_DIR = "data/newegg_scrape_data"
ITEMS_DIR = join(DATA_DIR, "items")
MAPS_DIR = join(DATA_DIR, "maps")
REVIEWS_DIR = join(DATA_DIR, "reviews")
CATEGORY_MAP_FN = join("data", "category_map.csv")
OUT_FN = join("data", "newegg_products.csv")


def load_review_map(fn):
    data = utils.load_csv(fn, skip_first=False)

    review_map = {}
    for row in data:
        review_map[row[0]] = (row[1], row[2])

    return review_map


def main():

    header = ["NID", "RID", "NAME", "CATEGORY", "PRICE", "NUM_REVIEWS", "BRAND", "INFO"]

    category_map = utils.load_category_map(CATEGORY_MAP_FN, dataset="newegg")

    base_fns = [f[6:] for f in os.listdir(ITEMS_DIR) if f.endswith(".csv")]

    with open(OUT_FN, "w") as f_out:

        writer = csv.writer(f_out, delimiter=",")
        writer.writerow(header)

        for base_fn in base_fns:

            category = category_map[base_fn[:-4]]

            if category in ["Keyboards", "Graphics Cards", "Monitors"]:
                continue

            items_fn = join(ITEMS_DIR, "items-" + base_fn)
            map_fn = join(MAPS_DIR, "map-" + base_fn)
            reviews_fn = join(MAPS_DIR, "reviews-" + base_fn)

            review_map = load_review_map(map_fn)
            items = utils.load_csv(items_fn, skip_first=False)

            for item in items:

                nid = item[0]

                try:
                    rid = review_map[nid][0]
                except KeyError as e:
                    # print("NID {} not found in review map ({})".format(nid, base_fn[:-4]))
                    continue

                num_reviews = review_map[nid][1]
                name = item[1]
                # make name lowercase
                name = name.lower()
                name = re.sub("\(|\)|\\|/|\[|\]|:|;|\||,", " ", name)

                price_dollars = item[2]
                price_cents = item[3]
                price = price_dollars + price_cents

                brand = item[5]
                # None filter
                if brand == "None":
                    brand = ""

                # make brand lowercase
                brand = brand.lower()

                # apply brand map
                brand = brands.map_newegg_brand(brand)

                info = item[6]
                # None filter
                if info == "None":
                    info = ""
                info = info.lower()
                info = re.sub("\(|\)|\\|/|\[|\]|:|;|\||,", " ", info)

                # if we don't have a name, skip this item.
                if name == "":
                    continue

                new_item = [nid, rid, name, category, price, num_reviews, brand, info]

                writer.writerow(new_item)


if __name__ == "__main__":
    main()
