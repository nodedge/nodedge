import csv
import os.path
import shutil
from string import Template

configFile = "block_config.csv"
savePath = "../../nodedge/blocks/autogen/"

if __name__ == "__main__":
    # Create folder for generated blocks
    if not os.path.exists(savePath):
        os.makedirs(savePath)
    else:
        for filename in os.listdir(savePath):
            filepath = os.path.join(savePath, filename)
            for filename in os.listdir(savePath):
                filepath = os.path.join(savePath, filename)
                try:
                    shutil.rmtree(filepath)
                except OSError:
                    os.remove(filepath)

    # Read one line of the csv
    with open(configFile) as infile:
        reader = csv.DictReader(infile, delimiter=",")

        for row in reader:

            # Generate code
            with open("block_template.txt") as templateFile:
                inputData = templateFile.read()
            template = Template(inputData)

            outputData = template.substitute(**row)
            filename = f"{(row['operation_name'])}_block.py"
            libraryPath = os.path.join(savePath, row["library"])
            if not os.path.exists(libraryPath):
                os.makedirs(libraryPath)
            filePath = os.path.join(libraryPath, filename)
            outputFile = open(filePath, "w")
            outputFile.write(outputData)
            outputFile.close()

        templateFile.close()
    infile.close()

# TODO: Generate test for each block in a separated file
# TODO: Create two folders for blocks: autogen and custom
