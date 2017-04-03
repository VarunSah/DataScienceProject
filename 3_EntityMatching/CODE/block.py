import csv
import py_entitymatching as em
import pandas as pd
import os
# import numpy as np
import math

AMAZON_PRODUCTS_FN = "matching/dataset/amazon_products.csv"
NEWEGG_PRODUCTS_FN = "matching/dataset/newegg_products.csv"

DEBUG_OUT_FN = "output/debug_blocking.txt"
SURVIVING_TUPLE_PAIRS_FN = "output/blocked_pairs_final.csv"



def custom_block_func(ltuple, rtuple):
    try:
        if len(rtuple["INFO"]) > 5:
            if (rtuple["INFO"] in ltuple["NAME"]) or (rtuple["INFO"] in ltuple["INFO"]):
                return False
            else:
                return True
        else:
            return True
    except TypeError as e:
        return True


def main():

    # Load csv files as dataframes and set the key attribute in the dataframe
    amazon_products = em.read_csv_metadata(AMAZON_PRODUCTS_FN, key="ASIN")
    newegg_products = em.read_csv_metadata(NEWEGG_PRODUCTS_FN, key="NID")

    # print('Number of tuples in amazon_products: ' + str(len(amazon_products)))
    # print('Number of tuples in newegg_products: ' + str(len(newegg_products)))
    print("Number of tuples in A X B:", str(len(amazon_products) * len(newegg_products)))

    # down sample (not used here)
    # amazon_sample, newegg_sample = em.down_sample(amazon_products, newegg_products, 200, 1, show_progress=False)

    # blocking based on category (the most reliable for our dataset)
    ab = em.AttrEquivalenceBlocker()
    blocked = ab.block_tables(amazon_products, newegg_products, "CATEGORY", "CATEGORY",
                              l_output_attrs=["NAME", "INFO"], r_output_attrs=["NAME", "INFO"])
    

    print("Number of blocked tuples (after blocking on category):", len(blocked))

    # debug the blocker - are we discarding a lot of potential matches?
    # dbg = em.debug_blocker(blocked, amazon_products, newegg_products, output_size=200)
    # print(dbg.head())
    # # dbg.to_csv(DEBUG_OUT_FN)

    # there are a few mis-categorized products that match that we are discarding
    # with this blocking step. but, this number is very small.  In the first 5,
    # it looks like only 2 are really matches, and these are the most likely to match.
    # The similarities are pretty small.

    # blocking based on brand name (overlap)
    # brand names are best blocked using q-gram overlap
    # allow missing so as not to block any potentially matching pairs
    # ob = em.OverlapBlocker()
    # blocked = ob.block_candset(blocked,
    #                             "BRAND", "BRAND",
    #                             word_level=False,
    #                             q_val=3,
    #                             overlap_size=2,
    #                             show_progress=False,
    #                             allow_missing=True,
    #                             n_jobs=-1)

    ab2 = em.AttrEquivalenceBlocker()
    blocked = ab2.block_candset(blocked, "BRAND", "BRAND", allow_missing=True)
#     blocked = ab.block_tables(amazon_products, newegg_products, "BRAND", "BRAND",
#                             l_output_attrs=["NAME", "INFO"], r_output_attrs=["NAME", "INFO"], allow_missing=True)

    print("Number of blocked tuples (after blocking on brand):", len(blocked))
    # print(blocked.head(10))

    # debug again
    # dbg = em.debug_blocker(blocked, amazon_products, newegg_products, output_size=200)
    # print(dbg.head())

    # at this point i realized that "western digital" brand shows up as "wd" in many
    # items on newegg, so I added it to clean brands

    # after fixing that, i realized that "gaming mice" and "mice" have some cross-listed products between
    # the two sites, eg. amazon has a specific mouse listed under "mice" while newegg puts it under "gaming mice"
    # but this is not too much of a problem

    # setup for rules based blocker
    block_t = em.get_tokenizers_for_blocking()
    block_s = em.get_sim_funs_for_blocking()
    atypes1 = em.get_attr_types(amazon_products)
    atypes2 = em.get_attr_types(newegg_products)
    block_c = em.get_attr_corres(amazon_products, newegg_products)
    block_f = em.get_features(amazon_products, newegg_products, atypes1, atypes2, block_c, block_t, block_s)
    #'jaccard(wspace(ltuple.NAME), wspace(rtuple.NAME))'
    #'overlap_coeff(wspace(ltuple.NAME), wspace(rtuple.NAME))'

    # JACCARD SCORE BETWEEN THE NAMES
    r1 = em.get_feature_fn('jaccard(wspace(ltuple.NAME), wspace(rtuple.NAME))', block_t, block_s)
    # weird workaround for weird bug
    r1["right_attribute"] = "NAME"
    r1["left_attribute"] = "NAME"
    em.add_feature(block_f, 'name_name_jac', r1)

    # OUR CUTOM RULE
    # em.add_blackbox_feature(block_f, 'custom_block', custom_block_func)
    # # block_f.function_source[29] = "ASDF"
    #
    # # weird workaround shows its ugly face again
    # # block_f.loc[29,"right_attribute"] = "NAME"
    # # block_f.loc[29,"left_attribute"] = "NAME"
    #
    # # block on name using rule based blocker (jaccard)

    rb = em.RuleBasedBlocker()
    rb.add_rule(["name_name_jac(ltuple, rtuple) < 0.5"], block_f)
    # rb.add_rule(["custom_block(ltuple, rtuple) > 0"], block_f)
    
    blocked_rule = rb.block_candset(blocked, n_jobs=1)
    print("Tuples after blocking on name: {}".format(len(blocked_rule)))

    bb = em.BlackBoxBlocker()
    bb.set_black_box_function(custom_block_func)
    blocked_black = bb.block_candset(blocked, n_jobs=1)


    print("Tuples after blocking on custom: {}".format(len(blocked_black)))

    blocked = em.combine_blocker_outputs_via_union([blocked_rule, blocked_black])
#     blocked = blocked_black

    # block on name using overlap blocker
    # ob = em.OverlapBlocker()
    # blocked = ob.block_candset(blocked, "NAME", "NAME",
    #                            word_level=True,
    #                            overlap_size=3,
    #                            show_progress=False,
    #                            allow_missing=False,
    #                            n_jobs=-1)
    print("Number of blocked tuples (after union):", len(blocked))

    # debug again
    dbg = em.debug_blocker(blocked, amazon_products, newegg_products, output_size=50, attr_corres=[('NAME', 'NAME')])
    print(dbg.head)

    # save surviving tuple pairs
    blocked.to_csv(SURVIVING_TUPLE_PAIRS_FN)


if __name__ == '__main__':
    main()