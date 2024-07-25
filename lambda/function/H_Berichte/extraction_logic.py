import time
import pandas as pd
import boto3
import tempfile
import os.path

from constants import Constants

def extraction_data(s3_bucket_name, s3_file_name):
    df = download_read_s3_file(s3_bucket_name, s3_file_name)
    return df

def download_read_s3_file(s3_bucket_name, s3_file_name):
    #Initiate s3 client
    s3_client = boto3.client('s3')

    #Initiate s3 resourse
    s3 = boto3.resource('s3')

    try:
        #Trigger data bucket
        basic_data_bucket = s3.Bucket(s3_bucket_name)
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            local_temp_path = tmpdir + "index.xlsx"
            basic_data_bucket.download_file(s3_file_name, local_temp_path)
            if os.path.isfile(local_temp_path):
                #Read the excel file
                raw_df = pd.read_excel(local_temp_path, sheet_name=Constants.read_sheet_index)
                final_df = manipulate_dataframe(raw_df)
                return final_df
            
    except Exception as e:
        print(e)

    return None


def manipulate_dataframe(df):
    df = df.dropna(how='all')
    print("number of rows in df: ", df.shape[0])
    df.rename(columns= Constants.columns_name, inplace = True)
    return df

