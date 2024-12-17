import pandas as pd
import numpy as np
import argparse
import os
import tanner_staging_validation

def update_female_df(female_df):
    # Python dictionaries mapping new values for adren_f calculation
    bodyhair_map = {1:1, 2:2, 3:4, 4:5}
    skin_map = {1:1, 2:2, 3:4, 4:5}
    height_map = {1:1, 2:2, 3:3, 4:5}
    breasts_map = {1:1, 2:3, 3:4, 4:5}
    mens_yn_map = {1:1, 2:5}
    # Mapping new values to the columns of the pandas df
    female_df["pq_pdms_height"] = female_df["pq_pdms_height"].map(height_map)
    female_df["pq_pdms_bodyhair"] = female_df["pq_pdms_bodyhair"].map(bodyhair_map)
    female_df["pq_pdms_skin"] = female_df["pq_pdms_skin"].map(skin_map)
    female_df["pq_pdms_f_breasts"] = female_df["pq_pdms_f_breasts"].map(breasts_map)
    female_df["pq_pdms_f_mens_yn"] = female_df["pq_pdms_f_mens_yn"].map(mens_yn_map)
    return female_df

def calc_adrenf(female_df_updated):
    female_df_updated["adrenarche_1"] = female_df_updated[["pq_pdms_bodyhair", "pq_pdms_skin"]].mean(axis=1)
    tmp_df = female_df_updated[female_df_updated["adrenarche_1"] == 1]
    female_df_updated["adrenarche_2"] = 1
    female_df_updated.loc[(female_df_updated["adrenarche_2"] == 1) & (female_df_updated["pq_pdms_bodyhair"] > 1),\
        "adrenarche_2"] = 2
    female_df_updated.loc[female_df_updated["adrenarche_1"] > 1.5, "adrenarche_2"] = 2
    female_df_updated.loc[female_df_updated["adrenarche_1"] > 2, "adrenarche_2"] = 3
    female_df_updated.loc[female_df_updated["adrenarche_1"] > 3, "adrenarche_2"] = 4
    female_df_updated.loc[female_df_updated["adrenarche_1"] > 4, "adrenarche_2"] = 5
    return(female_df_updated)

def calc_gonadf(female_df_adrenf):
    female_df_adrenf["gonad_1"] = female_df_adrenf[["pq_pdms_height", "pq_pdms_f_breasts"]].mean(axis=1)
    female_df_adrenf["gonad_2"] = 1
    mens_n_df = female_df_adrenf[female_df_adrenf["pq_pdms_f_mens_yn"] == 1]
    mens_n_df.loc[mens_n_df["gonad_1"] > 1.5, "gonad_2"] = 2
    mens_n_df.loc[mens_n_df["gonad_1"] > 2.5, "gonad_2"] = 3
    mens_n_df.loc[mens_n_df["gonad_1"] > 4, "gonad_2"] = 4
    mens_y_df = female_df_adrenf[female_df_adrenf["pq_pdms_f_mens_yn"] == 5]
    mens_y_df.loc[mens_y_df["gonad_1"] == 1, "gonad_2"] = 2
    mens_y_df.loc[mens_y_df["gonad_1"] > 1, "gonad_2"] = 3
    mens_y_df.loc[mens_y_df["gonad_1"] > 1.5, "gonad_2"] = 4
    mens_y_df.loc[mens_y_df["gonad_1"] > 3, "gonad_2"] = 5
    return pd.concat([mens_n_df,mens_y_df])

def update_male_df(male_df):
    bodyhair_map = {1:1, 2:2, 3:4, 4:5}
    skin_map = {1:1, 2:2, 3:3, 4:4}
    height_map = {1:1, 2:3, 3:4, 4:5}
    voice_map = {1:1, 2:2, 3:3, 4:5}
    male_df["pq_pdms_height"] = male_df["pq_pdms_height"].map(height_map)
    male_df["pq_pdms_bodyhair"] = male_df["pq_pdms_bodyhair"].map(bodyhair_map)
    male_df["pq_pdms_skin"] = male_df["pq_pdms_skin"].map(skin_map)
    male_df["pq_pdms_m_voice"] = male_df["pq_pdms_m_voice"].map(voice_map)
    return male_df

def calc_adrenm(male_df_updated):
    male_df_updated["adrenarche_1"] = male_df_updated[["pq_pdms_bodyhair", "pq_pdms_skin"]].mean(axis=1)
    male_df_updated["adrenarche_2"] = 1
    male_df_updated.loc[(male_df_updated["adrenarche_1"] > 1) & (male_df_updated["pq_pdms_skin"] > 1),\
        "adrenarche_2"] = 2
    male_df_updated.loc[male_df_updated["adrenarche_1"] > 1.5, "adrenarche_2"] = 2
    male_df_updated.loc[(male_df_updated["adrenarche_1"] > 2) & (male_df_updated["pq_pdms_bodyhair"] > 3),\
        "adrenarche_2"] = 3
    male_df_updated.loc[male_df_updated["adrenarche_1"] > 2.5, "adrenarche_2"] = 3
    male_df_updated.loc[male_df_updated["adrenarche_1"] > 3, "adrenarche_2"] = 4
    male_df_updated.loc[male_df_updated["adrenarche_1"] > 4, "adrenarche_2"] = 5
    return male_df_updated

def calc_gonadm(male_df_adrenm):
    male_df_adrenm["gonad_1"] = male_df_adrenm[["pq_pdms_height", "pq_pdms_m_voice"]].mean(axis=1)

    low_gonad_1_df = male_df_adrenm[male_df_adrenm["gonad_1"] < 3]
    low_gonad_1_df["gonad_2"] = low_gonad_1_df["gonad_1"].apply(np.floor)
    low_gonad_1_df.loc[low_gonad_1_df["pq_pdms_m_facehair"] > 1, "gonad_2"] += 1
    low_gonad_1_df.loc[(low_gonad_1_df["gonad_1"] == 2) & (low_gonad_1_df["pq_pdms_m_facehair"] == 1) & \
        (low_gonad_1_df["pq_pdms_m_voice"] == 1), "gonad_2"] = 1

    high_gonad_1_df = male_df_adrenm[male_df_adrenm["gonad_1"] > 2.5]
    high_gonad_1_df["gonad_2"] = high_gonad_1_df["gonad_1"].apply(np.ceil)
    high_gonad_1_df.loc[high_gonad_1_df["pq_pdms_m_facehair"] > 2, "gonad_2"] += 1

    frames = [low_gonad_1_df, high_gonad_1_df]
    male_df_gonadm = pd.concat(frames)
    return male_df_gonadm






def main(args):
    male_df, female_df, err_df = tanner_staging_validation.main(args)

    female_df_updated = update_female_df(female_df)
    female_df_adrenf = calc_adrenf(female_df_updated)
    female_df_final = calc_gonadf(female_df_adrenf)
    female_df_final["PDS Score"] = female_df_final[["adrenarche_2", "gonad_2"]].mean(axis=1)

    male_df_updated = update_male_df(male_df)
    male_df_adrenm = calc_adrenm(male_df_updated)
    male_df_final = calc_gonadm(male_df_adrenm)
    male_df_final["PDS Score"] = male_df_final[["adrenarche_2", "gonad_2"]].mean(axis=1)

    frames = [female_df_final, male_df_final]
    final_df = pd.concat(frames)
    final_df.to_csv("PDS_scores.csv", index = False)



if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", nargs=1, type=str, required=True,
                        help="Path to csv with data.")
    parser.add_argument("-o", "--output", nargs=1, type=str, required=True,
                        help="Output path with outfile name.")
    args = parser.parse_args()
    main(args)