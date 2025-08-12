import pyarrow.parquet as pq
from datetime import datetime
from fastparquet import ParquetFile

def get_col_before_da(cacheData, FOLDER, symbol, col, da):
    try:
        if symbol not in cacheData:
            fname = f"{FOLDER}/{symbol}.parquet"
            # Read Parquet file into a table
            pf = ParquetFile(fname)
            df = pf.to_pandas()
            # Convert table to list of records (dictionaries)
            data = df.to_dict(orient='records')
            cacheData[symbol] = data
        else:
            data = cacheData[symbol]

        # Convert 'da' to a datetime object if it's a string
        if isinstance(da, str):
            da = datetime.strptime(da, '%Y-%m-%d')
        else:
            da = datetime.combine(da, datetime.min.time())

        # Filter data based on date range and deduplicate based on 'kikann'
        unique_data = {}
        
        for record in data:
            record_date = record['da']
            if record_date < da:
                unique_data = record

        return unique_data[col]
    except Exception as e:
        # Logging error for debugging
        # print(f"Error with symbol {symbol}: {e}")
        return -1

def get_col_arr_before_da(cacheData, FOLDER, symbol, col, da):
    try:
        if symbol not in cacheData:
            fname = f"{FOLDER}/{symbol}.parquet"
            # Read Parquet file into a table
            # table = pq.read_table(fname)
            pf = ParquetFile(fname)
            # Convert table to list of records (dictionaries)
            data = pf.to_pandas().to_dict(orient='records')
            cacheData[symbol] = data
        else:
            data = cacheData[symbol]

        # Convert 'da' to a datetime object if it's a string
        if isinstance(da, str):
            da = datetime.strptime(da, '%Y-%m-%d')
        else:
            da = datetime.combine(da, datetime.min.time())

        # Collect values from the specified column where the date is before 'da'
        values = [float(record[col]) for record in data if record['da'] < da]

        return values

    except Exception as e:
        # Logging error for debugging
        # print(f"Error with symbol {symbol}: {e}")
        return []  # Return an empty list on error
