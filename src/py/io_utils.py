import glob
import os
import pandas as pd


def init_folders(dirs):
    """
    Create output directories if they don't exist.

    Parameters:
    - dirs: List of directory paths to be created.

    Returns:
    - None
    """
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)
            print(f"Created output directory: {dir}")

def read_data(input_dir):
    """
    Read input files from a directory.

    Parameters:
    - input_dir: Directory path containing the input files.

    Returns:
    - List of input file paths.
    """
    input_files = glob.glob(os.path.join(input_dir, '*'))
    input_files.sort()
    return input_files

def get_dfs(questions_dir, static_filename="static_q_and_a.csv",
            truth_filename="q_and_a_truth.csv", audience_filename="q_and_a_audience.csv"):
    """
    Load and join dataframes from question files.

    Parameters:
    - questions_dir: Directory path containing the question files.
    - static_filename: Filename of the static question and answer file. 
        Default is "static_q_and_a.csv".
    - audience_filename: Filename of the audience question and answer file. 
        Default is "q_and_a_audience.csv".

    Returns:
    - Joined dataframe of static and audience questions.
    """
    collected_csv_path = os.path.join(questions_dir, audience_filename)
    static_csv_path = os.path.join(questions_dir, static_filename)
    truth_csv_path = os.path.join(questions_dir, truth_filename)
    collected_df = translate_data(collected_csv_path)
    static_df = translate_data(static_csv_path)
    truth_df = translate_data(truth_csv_path)
    collected_df["ratio_diff"] = truth_df["ratio"] - collected_df["ratio"]
    static_df["ratio_diff"] = 0
    joined_df = pd.concat([collected_df, static_df])
    return joined_df

def translate_data(csv_path, sep="|"):
    """
    Read and translate data from a CSV file.
# 
    Parameters:
    - csv_path: Path to the CSV file.
    - sep: Separator used in the CSV file. Default is "|".

    Returns:
    - Translated dataframe with added "ratio" column.
    """
    df = pd.read_csv(csv_path, sep=sep)
    ratios = []
    for number in df["numbers"]:
        if '%' in number:
            value = number.replace("%", "")
            ratio = float(value) / 100
        elif 'jours' in number:
            ratio = 1.0
        else:
            value = int(number)
            length = len(str(value))
            max_length = int('9' * length)
            ratio = value / max_length
        ratios.append(ratio)
    df["ratio"] = ratios
    return df

