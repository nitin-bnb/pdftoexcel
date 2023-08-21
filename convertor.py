import tabula
import pandas as pd
from utils import processNetwest, readandcleandata, processLLoyds, processLLoyds2, processHSBC

def convert(file, filename):


    if filename == "Natwest":
        data = tabula.read_pdf(file, stream=True, guess=True, pages='all', multiple_tables=True, pandas_options={'header': None})
        processNetwest(data, filename)
    elif filename == "LLoyds Bank":
        processLLoyds(file, filename)
    elif filename == "LLoyds Bank 2":
        data = tabula.read_pdf(file, stream=True, guess=True, pages='all', multiple_tables=True, pandas_options={'header': None})
        processLLoyds2(data, filename)
    elif filename == "HSBC":
        data = tabula.read_pdf(file, stream=True, guess=True, pages='all', multiple_tables=True, pandas_options={'header': None})
        df = readandcleandata(data)
        df.columns = ['Date', 'Description', 'Paid In', 'Paid Out', 'Balance']
        processHSBC(df, filename)
    else:
        data = tabula.read_pdf(file, stream=True, guess=True, pages='all', multiple_tables=True, pandas_options={'header': None})
        df = readandcleandata(data)
        df = pd.concat(data, ignore_index=True)
        df.columns = ['Date', 'Description', 'Paid In', 'Paid Out', 'Balance']
  
    return ''