import tabula
from utils import processNetwest, processLLoyds, processLLoyds2, processHSBC, processBarclays, processHSBC_Scanned
from flask import Response

def convert(file, filename):

    if filename == "Natwest":
        data = tabula.read_pdf(file, stream=True, guess=True, pages='all', multiple_tables=True, pandas_options={'header': None})
        response = processNetwest(data, filename)
    elif filename == "LLoyds Bank":
        response = processLLoyds(file, filename)
    elif filename == "LLoyds Bank 2":
        data = tabula.read_pdf(file, stream=True, guess=True, pages='all', multiple_tables=True, pandas_options={'header': None})
        response =  processLLoyds2(data, filename)
    elif filename == "HSBC":
        response = processHSBC(file, filename)
    elif filename == 'Barclays Bank':
        data = tabula.read_pdf(file, stream=True, guess=True, pages='all', multiple_tables=True, pandas_options={'header': None})
        response = processBarclays(data,filename)
    elif filename == 'HSBC Scanned':
        response = processHSBC_Scanned(data, filename)
    else:
        return Response(status=404)
    return response