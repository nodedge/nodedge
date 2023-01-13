import csv
import json


def csv_to_json(csvFilePath, jsonFilePath):
    jsonArray = []

    # read csv file
    with open(csvFilePath, encoding="utf-8") as csvf:
        # load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf, delimiter=";")

        # convert each csv row into python dict
        for row in csvReader:
            # add this python dict to json array
            jsonArray.append(row)

    # convert python jsonArray to JSON String and write to file
    with open(jsonFilePath, "w", encoding="utf-8") as jsonf:
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)


if __name__ == "__main__":
    # csvFilePath = r"numpy_block_config.csv"
    csvFilePath = r"operator_block_config.csv"
    jsonFilePath = csvFilePath.replace("csv", "json")
    csv_to_json(csvFilePath, jsonFilePath)

    # with open(jsonFilePath, "r") as f:
    #     json = json.load(f)
    #     print(json)
    #
    #     for block in json:
    #         print(block)
