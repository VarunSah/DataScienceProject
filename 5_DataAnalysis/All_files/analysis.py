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
        # print e
        from IPython import embed; embed()
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
                    if e["name"]!= None:
                        result.append(e)
        except:
            print f
            continue


    with open(filename, "wb") as outfile:
         json.dump(result, outfile)




if __name__ == '__main__':

    path_to_json = 'bnode/'
    lst = [["asin", "name", "brand", "category", "price", "review_count", "info"]]
    for root, dirs, files in os.walk(path_to_json):
        for filename in files:
            # with open(os.path.join(root, file), "r") as auto:
            lst = extract_info(os.path.join(root, filename), lst)

    write_csv(lst, "amazon.csv")
    # json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
            # filename = "test.json"
    # merge_json('merger', filename)
    # lst = [["asin", "name", "brand", "category", "price", "review_count", "info"]]
    # for filename in json_files:
    #   print filename;
    #   lst = extract_info(path_to_json + filename, lst)

    

    # labels = ["ID", "ASIN", "DESCRIPTION"]
    # descriptionList = [labels]
    # descriptionList = extract_description(filename, descriptionList)
    # write_csv(descriptionList, "text/total.csv")

    # labels = ["ID", "ASIN", "NAME", "CATEGORY", "BRAND", "RATINGS", 
    #   "REVIEW_COUNT", "QUESTION_COUNT", "ORIGINAL_PRICE", "SALE_PRICE", "AVAILABILITY", "DESCRIPTION"]
    # productList = [labels]
    # productList = extract_info("product1.json", labels, productList)
    # write_csv(productList, "product1.csv")

    # path_to_json = 
    # json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    # print json_files  # for me this prints ['foo.json']
    
    