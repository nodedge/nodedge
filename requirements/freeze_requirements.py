import os


def freeze(input_path, name):
    output_name = input_path + "/freeze/" + name.split(".")[0] + ".txt"
    input_name = input_path + "/packages/" + name
    command = f"pip freeze -l -r {input_name} > {output_name}"
    os.system(command)

    with open(output_name, "r") as f:
        requirements = f.read()
        requirements = requirements.split("##")[0]
    with open(output_name, "w") as f:
        f.write(requirements)


if __name__ == "__main__":
    requirements_packages_path = "requirements"
    for name in os.listdir(requirements_packages_path + "/packages"):
        freeze(requirements_packages_path, name)
