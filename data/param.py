import pickle, yaml

def get_dict_params_name():

    with open(r"files/dict_parameters.yaml", "r") as file:
        dict_params_name: dict = yaml.safe_load(file)

    return dict_params_name

def get_dict_params_label(dict_params_name: dict) -> dict:

    dict_params_label = {}

    for key, value in dict_params_name.items():
        dict_aux1 = {"name": key}
        dict_aux2 = {sub_key: sub_value for sub_key, sub_value in value.items() if sub_key != "columnLabel"}
        dict_params_label[value["columnLabel"]] = {**dict_aux1, **dict_aux2}

    return dict_params_label

DICT_PARAMS_NAME = get_dict_params_name()
DICT_PARAMS_LABEL = get_dict_params_label(DICT_PARAMS_NAME)
DICT_NASA_LABEL = {value["NASALabel"]: key for key, value in DICT_PARAMS_LABEL.items()}






    


