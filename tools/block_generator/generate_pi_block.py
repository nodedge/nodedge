import csv
import os.path
from string import Template

config_file = "block_config.csv"
save_path = "./generated_blocks/"

if __name__ == "__main__":
    # Create folder for generated blocks
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Read one line of the csv
    with open(config_file) as infile:
        reader = csv.DictReader(infile, delimiter=",")

        for row in reader:

            # Generate code
            with open("pi_block_template.txt") as template_file:
                input_data = template_file.read()
            template = Template(input_data)

            output_data = template.substitute(**row)
            file_name = f"{row['operation_name']}_block.py"
            file_path = os.path.join(save_path, file_name)
            output_file = open(file_path, "w")
            output_file.write(output_data)
            output_file.close()

        template_file.close()
    infile.close()

# TODO: Generate test for each block in a separated file
# TODO: Create two folders for blocks: autogen and custom
