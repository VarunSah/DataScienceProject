""" Utility functions """

# python
import csv


def load_csv(fn, skip_first=False):

    data = []

    with open(fn, "r") as f_handle:
        reader = csv.reader(f_handle, delimiter=",")

        if skip_first:
            next(reader)

        for row in reader:
            # ignore blank rows (for some reason the amazon csv has a lot of these)
            if row:
                data.append(row)

    return data


def load_category_map(fn, dataset="amazon"):

    if dataset == "amazon":
        cat_idx = 2
    elif dataset == "newegg":
        cat_idx = 1

    data = load_csv(fn, skip_first=True)

    category_map = {}
    for row in data:
        cats = [x.strip() for x in row[cat_idx].split(",")]
        for cat in cats:
            category_map[cat] = row[0]

    return category_map
