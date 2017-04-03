import pandas
import py_entitymatching as em

AMAZON_PRODUCTS_FN = "data/amazon_products.csv"
NEWEGG_PRODUCTS_FN = "data/newegg_products.csv"
BLOCKED_PAIRS_FN = "output/blocked_pairs_details.csv"
LABELED_PAIRS_FN = "output/labeled_pairs_details.csv"

def main():

    amazon_products = em.read_csv_metadata(AMAZON_PRODUCTS_FN, key='ASIN')
    newegg_products = em.read_csv_metadata(NEWEGG_PRODUCTS_FN, key='NID')
    blocked_pairs = em.read_csv_metadata(BLOCKED_PAIRS_FN, key='_id',
                             fk_ltable='ltable_ASIN', fk_rtable='rtable_NID',
                             ltable=amazon_products, rtable=newegg_products, encoding='utf-8')

    print(blocked_pairs.head())

    # create a subsample of blocked pairs
    sample = em.sample_table(blocked_pairs, 450)

    labeled_sample = em.label_table(sample, "label")
    
    labeled_sample.to_csv(LABELED_PAIRS_FN, sep = ',')
    

if __name__ == "__main__":
    main()