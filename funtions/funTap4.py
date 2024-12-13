import pandas as pd
import numpy as np
import datetime as dt


def name_file_head(name: str) -> str:
    now = dt.datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def valid_options(df: pd.DataFrame, dict_parameters: dict) -> list:

    return [dict_parameters[key] for key in dict_parameters if dict_parameters[key] in df.columns.tolist()]