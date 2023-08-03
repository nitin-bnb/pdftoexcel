import tabula
import pandas as pd
from utils import processNetwest, readandcleandata, processLLoyds, processLLoyds2, processHSBC

def convert(file, filename):

    data = tabula.read_pdf(file, stream=True, guess=True, pages='all', multiple_tables=True, pandas_options={'header': None})
    if data:
        df = readandcleandata(data)
        # Add column names to the DataFrame
        if filename == "Natwest":
            df.columns = ['Date', 'Description', 'Type', 'Paid In', 'Paid Out', 'Ledger Balance']  
            processNetwest(df, filename)  
        elif filename == "LLoyds Bank":
            df.columns = ['Date', 'Activity', 'Paid Out', 'Paid In', 'Balance']
            processLLoyds(df, filename)
        elif filename == "LLoyds Bank 2":
            df.columns = ['Date', 'Description', 'Type', 'Paid In', 'Paid Out', 'Balance']
            processLLoyds2(df, filename)
        elif filename == "HSBC":
            df.columns = ['Date', 'Description', 'Paid In', 'Paid Out', 'Balance']
            processHSBC(df, filename)
        else:
            df = pd.concat(data, ignore_index=True)
            df.columns = ['Date', 'Description', 'Paid In', 'Paid Out', 'Balance']

    #     
    return ''