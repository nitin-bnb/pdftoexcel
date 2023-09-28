import tabula
from utils import processNatwest, processLLoyds, processLLoyds2, processHSBC, processBarclays, processHSBC_Scanned, processNatwest_Large_Scanned, processNatwest_Small_Scanned
# , processBarclays_Scanned
from flask import Response

def convert(file, filename):

    if filename == "Natwest":
        data = tabula.read_pdf(file, stream=True, guess=True, pages='all', multiple_tables=True, pandas_options={'header': None})
        response = processNatwest(data, filename)
    elif filename == "LLoyds Bank":
        response = processLLoyds(file, filename)
    elif filename == "LLoyds Bank 2":
        response =  processLLoyds2(file, filename)
    elif filename == "HSBC":
        response = processHSBC(file, filename)
    elif filename == 'Barclays Bank':
        data = tabula.read_pdf(file, stream=True, guess=True, pages='all', multiple_tables=True, pandas_options={'header': None})
        response = processBarclays(data,filename)
    elif filename == 'HSBC Scanned':
        response = processHSBC_Scanned(file , filename)
    elif filename == 'Natwest Large Scanned':
        response = processNatwest_Large_Scanned(file, filename)
    elif filename == 'Natwest Small Scanned':
        print(">>>>>>>>>> filename", filename)
        response = processNatwest_Small_Scanned(file, filename)
        print(">>>>>> response", response)
    # elif filename == 'Barclays Bank Scanned':
    #     response = processBarclays_Scanned(file, filename)
    else:
        return Response(status=404)
    return response