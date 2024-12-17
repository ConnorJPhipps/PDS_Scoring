# Takes a spreadsheet with

import pandas as pd
import numpy as np
import argparse
import os

def validate_path(path):
    path_decomp = path.split("/")
    fname = path_decomp.pop()
    if path_decomp:
        dir_path = os.path.join(*path_decomp)
    else:
        dir_path = ""
    dir_bool = True
    file_bool = True
    if not os.path.exists(dir_path) and path_decomp:
        dir_bool = False
    if not os.path.exists(path):
        file_bool = False
    return [dir_bool, file_bool]

def check_gender(input_df):
    gen_clean_df = input_df
    gen_error_df = pd.DataFrame(columns=gen_clean_df.columns)
    data_overflow = input_df[(input_df["pq_pdms_f_breasts"].notna() | input_df["pq_pdms_f_mens_yn"].notna())
                                 &
                                 (input_df["pq_pdms_m_voice"].notna() | input_df["pq_pdms_m_facehair"].notna())]
    data_dirth = input_df[(input_df["pq_pdms_f_breasts"].isnull() | input_df["pq_pdms_f_mens_yn"].isnull())
                             &
                (input_df["pq_pdms_m_voice"].isnull() | input_df["pq_pdms_m_facehair"].isnull())]
    gen_check_list = data_overflow["study_id"].to_list() + data_dirth["study_id"].to_list()
    if gen_check_list:
        gen_error_df = gen_clean_df[gen_clean_df["study_id"].isin(gen_check_list)]
        gen_clean_df = gen_clean_df[~gen_clean_df["study_id"].isin(gen_check_list)]
    return(gen_clean_df, gen_error_df)

def check_range(clean_gender_df):
    general_range = range(1,5)
    clean_df = clean_gender_df
    range_error_df = pd.DataFrame(columns=clean_df.columns)
    height = clean_gender_df[~clean_gender_df["pq_pdms_height"].isin(general_range)]
    body_hair = clean_gender_df[~clean_gender_df["pq_pdms_bodyhair"].isin(general_range)]
    skin = clean_gender_df[~clean_gender_df["pq_pdms_skin"].isin(general_range)]
    f_breasts = clean_gender_df[(clean_gender_df["pq_pdms_f_breasts"] < 1)
                           | (clean_gender_df["pq_pdms_f_breasts"] > 4)]
    f_mens = clean_gender_df[(clean_gender_df["pq_pdms_f_mens_yn"] < 1)
                            | (clean_gender_df["pq_pdms_f_mens_yn"] > 2)]
    m_voice = clean_gender_df[(clean_gender_df["pq_pdms_m_voice"] < 1)
                            | (clean_gender_df["pq_pdms_m_voice"] > 4)]
    m_face_hair = clean_gender_df[(clean_gender_df["pq_pdms_m_facehair"] < 1)
                            | (clean_gender_df["pq_pdms_m_facehair"] > 4)]
    range_check_list = (height["study_id"].tolist() + body_hair["study_id"].tolist() + skin["study_id"].tolist() +
                        f_breasts["study_id"].tolist() + f_mens["study_id"].tolist() +
                        m_voice["study_id"].tolist() + m_face_hair["study_id"].tolist())
    range_error_df = clean_gender_df[clean_gender_df["study_id"].isin(range_check_list)]
    clean_df = clean_gender_df[~clean_gender_df["study_id"].isin(range_check_list)]
    return(clean_df, range_error_df)

def gender_split(clean_data):
    missing_female = clean_data[
        (clean_data["pq_pdms_f_breasts"].isnull() & ~clean_data["pq_pdms_f_mens_yn"].isnull())
        | (~clean_data["pq_pdms_f_breasts"].isnull() & clean_data["pq_pdms_f_mens_yn"].isnull())]
    missing_male = clean_data[
        (clean_data["pq_pdms_m_voice"].isnull() & ~clean_data["pq_pdms_m_facehair"].isnull())
        | (~clean_data["pq_pdms_m_voice"].isnull() & clean_data["pq_pdms_m_facehair"].isnull())]
    gender_value_error = missing_female["study_id"].tolist() + missing_male["study_id"].tolist()
    if gender_value_error:
        gender_value_error_df = clean_data[clean_data["study_id"].isin(gender_value_error)]
        male_df = clean_data[clean_data["pq_pdms_f_breasts"].isnull() &
                             ~clean_data[clean_data["study_id"].isin(gender_value_error)]]
        female_df = clean_data[clean_data["pq_pdms_m_voice"].isnull() &
                               ~clean_data[clean_data["study_id"].isin(gender_value_error)]]
    else:
        gender_value_error_df = pd.DataFrame(columns=clean_data.columns)
        male_df = clean_data[clean_data["pq_pdms_f_breasts"].isnull()]
        female_df = clean_data[clean_data["pq_pdms_m_voice"].isnull()]
    return male_df, female_df, gender_value_error_df

def validate_data(in_file):
    input_df = pd.read_csv(in_file)
    columns_of_interest = ["study_id",
               "pq_pdms_height", "pq_pdms_bodyhair", "pq_pdms_skin",
               "pq_pdms_f_breasts", "pq_pdms_f_mens_yn",
               "pq_pdms_m_voice", "pq_pdms_m_facehair"]
    input_df = input_df[columns_of_interest]
    # GOOD print(input_df.head())
    clean_gender_df, gender_error_df = check_gender(input_df)
    # GOOD print(clean_gender_df.head())
    clean_data, out_of_range_data = check_range(clean_gender_df)
    male_df, female_df, gender_value_error_df = gender_split(clean_data)
    net_err_list = list(set(
        list(gender_error_df["study_id"]) +
        list(out_of_range_data["study_id"]) +
        list(gender_value_error_df["study_id"])
    ))
    net_err_df = input_df[input_df["study_id"].isin(net_err_list)]
    return(male_df, female_df, net_err_df)


def main(args):
    # Check input path and files
    input_dir_bool, input_file_bool = validate_path(args.input[0])
    if not input_file_bool:
        print("The path to the input file is not valid.")
        exit()
    dir_bool, file_bool = validate_path(args.output[0])
    if not dir_bool:
        print("The output directory does not exist.")
        exit()
    if file_bool:
        print(args.output[0] + " already exists. Please move or delete file.")
        exit()
    male_df, female_df, net_err_df = validate_data(args.input[0])
    return male_df, female_df, net_err_df

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", nargs=1, type=str, required=True,
                        help="Path to csv with data.")
    parser.add_argument("-o", "--output", nargs=1, type=str, required=True,
                        help="Output path with outfile name.")
    args = parser.parse_args()
    main(args)