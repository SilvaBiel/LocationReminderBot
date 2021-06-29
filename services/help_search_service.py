import re
import glob
import pathlib


def get_help_for_all_commands():
    result = ""
    all_founded_methods = []
    for filename in glob.iglob('**/**', recursive=True):

        if "help_search_service.py" in filename:
            continue

        extension = pathlib.Path(filename).suffix
        if extension == ".py":
            file_object = open(filename)
            data = file_object.read()
            file_object.close()

            regex_string = '/help/(.*?)/help/'

            if re.findall(regex_string, data):
                help_data = re.findall(regex_string, data, re.DOTALL)
                if help_data:
                    all_founded_methods.extend(help_data)

    for data in all_founded_methods:
        if re.search("[a-zA-Z]", data):

            if "\n" in data:
                data = data.replace("\n", "")

            if "    " in data:
                data = data.replace("    ", "")

            data = data + "\n\n"
            result += data

    return result