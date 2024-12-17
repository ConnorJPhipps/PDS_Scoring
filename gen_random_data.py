import pandas as pd
import numpy as np
import argparse

from numpy.distutils.mingw32ccompiler import rc_name

NUM_ROWS = 100

# Variables
#   pq_pdms_height: [1-4]
#   pq_pdms_bodyhair: [1-4]
#   pq_pdms_skin: [1-4]
#   pq_pdms_f_breasts: [1-4]
#   pq_pdms_m_voice: [1-4]
#   pq_pdms_m_facehair: [1-4]]
#   pq_pdms_f_mens_yn: [1, 2]

def gen_random_sub(sub, gender):
    pq_pdms_height = np.random.randint(1,5)
    pq_pdms_bodyhair = np.random.randint(1, 5)
    pq_pdms_skin = np.random.randint(1, 5)
    pq_pdms_m_voice = np.nan
    pq_pdms_m_facehair = np.nan
    pq_pdms_f_breasts = np.nan
    pq_pdms_f_mens_yn = np.nan
    # Male
    if gender:
        pq_pdms_m_voice = np.random.randint(1, 5)
        pq_pdms_m_facehair = np.random.randint(1, 5)
    # Female
    else:
        pq_pdms_f_breasts = np.random.randint(1, 5)
        pq_pdms_f_mens_yn = np.random.randint(1, 3)
    rand_sub_data = [sub,
                     pq_pdms_height, pq_pdms_bodyhair, pq_pdms_skin,
                     pq_pdms_f_breasts, pq_pdms_f_mens_yn,
                     pq_pdms_m_voice, pq_pdms_m_facehair]
    return(rand_sub_data)

def main(args):
    columns = ["study_id",
               "pq_pdms_height", "pq_pdms_bodyhair", "pq_pdms_skin",
               "pq_pdms_f_breasts", "pq_pdms_f_mens_yn",
               "pq_pdms_m_voice", "pq_pdms_m_facehair"]
    rand_df = pd.DataFrame(columns=columns)
    for sub in range(0, args.num[0]):
        gender = np.random.choice([True, False])
        rand_df.loc[sub] = gen_random_sub(sub, gender)
    rand_df.to_csv(args.output[0], index=False)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num", nargs=1, type=int, required=True,
                        help="The number of subjects to generate.")
    parser.add_argument("-o", "--output", nargs=1, type=str, required=True,
                        help="Output path with outfile name.")
    args = parser.parse_args()
    main(args)