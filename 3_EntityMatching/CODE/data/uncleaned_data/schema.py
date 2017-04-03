import json
import csv
import glob
import os

def extract_info(filename, lst):
    fields = ["asin", "name", "brand", "category", "price", "review_count", "info"]
    try:
        objLst = json.loads(open(filename).read())

        for obj in objLst:
            row = []
            for label in fields:
                info = extract_label(obj, label);
                row.append(info)

            lst.append(row)

    except Exception as e:
        return lst

    return lst

def extract_label(obj, label):
    d = obj[label]
    if d == None:
        info = ""
    else:
        info = str(d.encode('ascii', 'ignore').decode('ascii'))

    return info

def extract_document(filename):
    count = 276
    try:
        objLst = json.loads(open(filename).read())
        for obj in objLst:
            count += 1
            asin = str(obj['ASIN'])
            d  = obj['DESCRIPTION']
            if d == None:
                continue
            description = str(d.encode('ascii', 'ignore').decode('ascii'))
            txtname = 'text/' + str(count) + "_" + asin + ".txt"
            f = open(txtname,"w")
            f.write(description)
            f.close()
    except Exception as e:
        print(e)
        # from IPython import embed; embed()


def write_csv(lst, filename):
    csvFile = open(filename, 'w')
    # Create Writer Object
    wr = csv.writer(csvFile, dialect='excel')
    # # Write Data to File
    for item in lst:
        wr.writerow(item)


def merge_json(folder, filename):
    result = []
    for f in glob.glob(folder + "/*.json"):
        try:
            with open(f, "rb") as infile:
                obj = json.load(infile)
                for e in obj:
                    if e["NAME"]!= None:
                        result.append(e)
        except:
            continue


    with open(filename, "wb") as outfile:
         json.dump(result, outfile)


if __name__ == '__main__':

    print("in main")
    path_to_json = 'amazon_scrape_data/'
    lst = [["asin", "name", "brand", "category", "price", "review_count", "info"]]
    for root, dirs, files in os.walk(path_to_json):
        for filename in files:
            # with open(os.path.join(root, file), "r") as auto:
            lst = extract_info(os.path.join(root, filename), lst)

    write_csv(lst, "amazon.csv")