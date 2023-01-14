import csv
import json
import logging
import os.path
import shutil
from string import Template
from typing import Dict, List

from black import FileMode, format_str

logger = logging.getLogger(__name__)

# Parameters to set before running the block generation
libraryTitle = "maths"  # string of library to generate
configFile = "numpy_block_config.json"  # config file
savePath = "../../nodedge/blocks/autogen"  # path where to save the generated blocks
overwrite = True  # True to overwrite, False otherwise
initFilename = "__init__.py"
firstCode = 16
opNodeFilename = "op_node.py"


def _prepend_socket_type(types_string):
    types_string = types_string[1:-1]  # remove parenthesis
    types_list = types_string.split(",")
    types_string = (
        "[" + ", ".join(["SocketType." + currType for currType in types_list]) + ",]"
    )

    return types_string


def _generate_common_init_file(libraryDict, savePath, initFilename):
    # Create init file
    initFileString = ""
    for lib in sorted(libraryDict.keys()):
        initFileString += f"from .{lib} import *\n"
    initFilePath = os.path.join(savePath, initFilename)
    initFile = open(initFilePath, "w")
    initFileString = format_str(initFileString, mode=FileMode())
    initFile.write(initFileString)
    initFile.close()


def _generate_init_files(libraryDict, savePath, initFilename):
    # Create init file for each autogenerated library
    initFileString = ""
    for lib, blockList in libraryDict.items():
        for blockName in sorted(blockList):
            initFileString += f"from .{blockName}_block import *\n"
        initFilePath = os.path.join(savePath, lib, initFilename)
        initFile = open(initFilePath, "w")
        initFileString = format_str(initFileString, mode=FileMode())
        initFile.write(initFileString)
        initFile.close()


def _init_lib_path(savePath, lib):
    # Create `autogen/<lib>` folder for generated block libraries
    if not os.path.exists(savePath):
        os.makedirs(savePath)
    # `autogen` lib already exists
    else:
        # Delete lib to be overwritten
        if overwrite:
            libPath = os.path.join(savePath, lib)
            try:
                shutil.rmtree(libPath)
            except OSError:
                logger.warning(f"Lib path does not exist: {libPath}")
                # os.remove(libPath)


def _create_blocks(configFile, savePath, lib):
    with open(configFile) as infile:
        if "csv" in configFile:
            reader = csv.DictReader(infile, delimiter=";")
        elif "json" in configFile:
            reader = json.load(infile)
        else:
            raise ValueError(f"Invalid config file format: {configFile}")
        libraries: Dict[str, List[str]] = {}
        opBlockNames: Dict[str, List[str]] = {}

        # Read one line (corresponding to one block) from the csv
        for row in reader:

            # Give a warning if
            if row["library_title"] == lib:

                # Save block in dictionary
                if row["library"] not in libraries.keys():
                    libraries[row["library"]] = [row["function"]]
                    opBlockNames[row["library"]] = [row["op_block_string"]]
                else:
                    libraries[row["library"]].append(row["function"])
                    opBlockNames[row["library"]].append(row["op_block_string"])

                # Add socket type object
                row["input_socket_types"] = _prepend_socket_type(
                    row["input_socket_types"]
                )
                row["output_socket_types"] = _prepend_socket_type(
                    row["output_socket_types"]
                )

                # Generate current block
                with open("block_template.txt") as templateFile:
                    inputData = templateFile.read()

                template = Template(inputData)

                outputData = template.substitute(**row)
                outputData = format_str(outputData, mode=FileMode())
                folder = f"{(row['function'])}_block.py"
                libraryPath = os.path.join(savePath, row["library_title"])
                if not os.path.exists(libraryPath):
                    os.makedirs(libraryPath)
                filePath = os.path.join(libraryPath, folder)
                outputFile = open(filePath, "w")
                outputFile.write(outputData)
                outputFile.close()
                templateFile.close()

            else:
                print(f"Skip function {row['function']} of library {row['library']}\n")
    infile.close()
    return libraries, opBlockNames


def _generate_config_file(opBlockNames, configFilename, code: int = 1):
    # Create init file
    fileString = ""
    for lib in sorted(opBlockNames.keys()):
        for op_block_name in opBlockNames[lib]:
            fileString += f"{op_block_name} = {code}\n"
            code += 1
    filePath = os.path.join(savePath, configFilename)
    configFile = open(filePath, "w")
    fileString = format_str(fileString, mode=FileMode())
    configFile.write(fileString)
    configFile.close()

    return


if __name__ == "__main__":
    _init_lib_path(savePath, libraryTitle)
    libraries, opBlockNames = _create_blocks(configFile, savePath, libraryTitle)
    # _generate_common_init_file(libraries, savePath, initFilename)
    _generate_init_files(libraries, savePath, initFilename)
    _generate_config_file(opBlockNames, opNodeFilename, firstCode)

# TODO: Generate test for each block in a separated file
