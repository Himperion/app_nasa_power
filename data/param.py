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
DICT_KEY_LABEL = {value["key"]: key for key, value in DICT_PARAMS_LABEL.items()}
DICT_WIND_LABEL = {"W10M": "Wind 10 m", "W50M": "Wind 50 m"}

DICT_TIME = {
    "dates (Y-M-D hh:mm:ss)": {
        "Name": "Fecha (A-M-D hh:mm:ss)"
    }
}
    
DICT_PARAMS = {
    "WD10M": {
        "Label": "Dwind 10 m (°)",
        "Name": "Dirección del viento a 10m (°)",
        "NASALabel": "WD10M",
        "Emoji": "🌬",
        "Color": "#00B3B3"
    },
    "WD50M": {
        "Label": "Dwind 50 m (°)",
        "Name": "Dirección del viento a 50m (°)",
        "NASALabel": "WD50M",
        "Emoji": "🌬",
        "Color": "#034D4D"
    },
    "ALLSKY_SFC_SW_DWN": {
        "Label": "Gin (W/m²)",
        "Name": "Irradiancia (W/m²)",
        "NASALabel": "ALLSKY_SFC_SW_DWN",
        "Emoji": "☀️",
        "Color": "#66C2C2"
    },
    "LOAD": {
        "Label": "Load (kW)",
        "Name": "Perfil de demanda eléctrica (kW)",
        "NASALabel": None,
        "Emoji": "💡",
        "Color": "#069494",
    },
    "T2M": {
        "Label": "Tamb (°C)",
        "Name": "Temperatura ambiente (°C)",
        "NASALabel": "T2M",
        "Emoji": "🌡",
        "Color": "#069458"
    },
    "TOPER": {
        "Label": "Toper (°C)",
        "Name": "Temperatura de operación del modulo fotovoltaico",
        "NASALabel": None,
        "Emoji": "🪛",
        "Color": "#8B0000"
    },
    "WS10M": {
        "Label": "Vwind 10 m (m/s)",
        "Name": "Velocidad del viento a 10 m (m/s):",
        "NASALabel": "WS10M",
        "Emoji": "🪁",
        "Color": "#00B3B3"
    },
    "WS50M": {
        "Label": "Vwind 50 m (m/s)",
        "Name": "Velocidad del viento a 50 m (m/s)",
        "NASALabel": "WS50M",
        "Emoji": "🪁",
        "Color": "#034D4D"
    },
    "W10M": {
        "Label": "Wind 10 m",
        "Emoji": "🪁",
        "Color": "#4169E1",
    },
    "W50M": {
        "Label": "Wind 50 m",
        "Emoji": "🪁",
        "Color": "#0044FF"
    }
}

DICT_PARAMS_WIND = {
    "W10M": {"WS": "WS10M", "WD": "WD10M", "Label": "Wind 10 m"},
    "W50M": {"WS": "WS50M", "WD": "WD10M", "Label": "Wind 50 m"},
}

DICT_PARAMS_LABEL_KEY = {value["Label"]: key for key, value in DICT_PARAMS.items()} 





    


