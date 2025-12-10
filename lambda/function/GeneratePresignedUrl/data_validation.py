from custom_exception import EmptyDataException

def check_empty_data(data, mmsg):
    if not data:
        raise EmptyDataException(mmsg)