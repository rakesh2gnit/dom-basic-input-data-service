import os

class Constants:
    dynamodb_resource = "dynamodb"

    #Dynamo Db Table name
    basic_data_h_berichte_table_name = os.environ.get("BASIC_DATA_H_BERICHTE_TABLE_NAME")

    #Partition Key
    partition_key = os.environ.get("PARTITION_KEY")

    #General Timestamp
    timestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    #Sheet index
    read_sheet_index = 0

    #Process Status
    process_done = "processed"
    process_failed = "failed"

    report_type = "H_Berichte"

    bucketName = "basic-data-poc"
    pkwHBerichte = "H_Berichte/PKW"

    #Success Message
    success_message_file_process = "- Model Year Report file is "

    #Column name
    columns_name = {
                    "BR":"br",
                    "AA":"aa",
                    "AJ/MOPF":"aj_mopf",
                    "AJ/MOPF-Paket":"aj_paket",
                    "Paket PU-Termin":"paket_pu_termin",
                    "Paket-Projektleiter":"paket_projektleiter",
                    "Bemerkung":"bemerkung",
                    "Paketname":"paketname",
                    "Paket-Status":"paket_status"
                    }