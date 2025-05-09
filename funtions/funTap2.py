import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

from funtions import general

def name_file_head(name: str) -> str:
    now = datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def get_label_params(dict_param: dict) -> str:

    return f"**{dict_param['label']}:** {dict_param['description']} {dict_param['unit']}"

def get_widget_number_input(label: str, variable: dict):

    return st.number_input(label=label, **variable)

def get_download_button(directory: str, name_file: str, format_file: str, description: str):

    with open(general.resource_path(f"{directory}/{name_file}.{format_file}"), "rb") as content_xlsx:
        st.download_button(label=f"📄 Descargar plantilla **:red[{description}]**:",
                           data=content_xlsx,
                           file_name=f"{name_file}.{format_file}",
                           mime=format_file)
                
    return

def check_dataframe_input(dataframe: pd.DataFrame, options: list):

    columns_options, columns_options_sel, columns_options_check = {}, {}, {}
    columns_options_drop, check = [], True

    header = dataframe.columns

    for key in options:
        list_options = options[key]
        columns_aux = []
        for column in header:
            if column in list_options:
                columns_aux.append(column)
        columns_options[key] = columns_aux

    for key in columns_options:
        list_columns_options = columns_options[key]
        if len(list_columns_options) != 0:
            columns_options_sel[key] = list_columns_options[0]
            columns_options_check[key] = True

            if len(list_columns_options) > 1:
                for i in range(1,len(list_columns_options),1):
                    columns_options_drop.append(options[i])

        else:
            columns_options_sel[key] = None
            columns_options_check[key] = False

    if len(columns_options_drop) != 0:
        dataframe = dataframe.drop(columns=columns_options_drop)

    for key in columns_options_check:
        check = check and columns_options_check[key]

    return dataframe, check, columns_options_sel

def get_column_Toper(dataframe: pd.DataFrame, options_sel: dict, NOCT: int, column_name: str) -> pd.DataFrame:

    dataframe[column_name] = dataframe[options_sel["Tamb"]] + (NOCT-20)*(dataframe[options_sel["Geff"]]/800)

    return dataframe

def to_excel(df: pd.DataFrame):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    
    processed_data = output.getvalue()
        
    return processed_data

def get_list_tabs_graph(list_data_columns: list, list_options_columns_name: list, list_options_columns_label: list):

    list_tabs_graph_name, list_tabs_graph_label = [], []
    for i in range(0,len(list_data_columns),1):
        if list_data_columns[i] in list_options_columns_name:
            list_tabs_graph_name.append(list_data_columns[i])
            list_tabs_graph_label.append(list_options_columns_label[list_options_columns_name.index(list_data_columns[i])])

    return list_tabs_graph_name, list_tabs_graph_label

def view_dataframe_information(dataframe: pd.DataFrame, dict_parameters: dict):

    listOptionsColumnsName = [dict_parameters[key]["columnLabel"] for key in dict_parameters]
    listOptionsColumnsLabel = [f"{dict_parameters[key]['emoji']} {dict_parameters[key]['columnLabel']}" for key in dict_parameters]

    list_tabs_graph_name, list_tabs_graph_label = get_list_tabs_graph(list(dataframe.columns),
                                                                      listOptionsColumnsName,
                                                                      listOptionsColumnsLabel)
     
    if len(list_tabs_graph_name) != 0:
        if len(list_tabs_graph_name) == 1:
            subtab_con1 = st.tabs(list_tabs_graph_label)
            list_subtab_con = [subtab_con1[0]]
        elif len(list_tabs_graph_name) == 2:
            subtab_con1, subtab_con2 = st.tabs(list_tabs_graph_label)
            list_subtab_con = [subtab_con1, subtab_con2]
        elif len(list_tabs_graph_name) == 3:
            subtab_con1, subtab_con2, subtab_con3 = st.tabs(list_tabs_graph_label)
            list_subtab_con = [subtab_con1, subtab_con2, subtab_con3]
        elif len(list_tabs_graph_name) == 4:
            subtab_con1, subtab_con2, subtab_con3, subtab_con4 = st.tabs(list_tabs_graph_label)
            list_subtab_con = [subtab_con1, subtab_con2, subtab_con3, subtab_con4]
        elif len(list_tabs_graph_name) == 5:
            subtab_con1, subtab_con2, subtab_con3, subtab_con4, subtab_con5 = st.tabs(list_tabs_graph_label)
            list_subtab_con = [subtab_con1, subtab_con2, subtab_con3, subtab_con4, subtab_con5]
        elif len(list_tabs_graph_name) == 6:
            subtab_con1, subtab_con2, subtab_con3, subtab_con4, subtab_con5, subtab_con6 = st.tabs(list_tabs_graph_label)
            list_subtab_con = [subtab_con1, subtab_con2, subtab_con3, subtab_con4, subtab_con5, subtab_con6]

        for i in range(0,len(list_subtab_con),1):
            with list_subtab_con[i]:
                st.line_chart(data=dataframe[[list_tabs_graph_name[i]]], y=list_tabs_graph_name[i])

    return