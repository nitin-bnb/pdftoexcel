from utils import processNatwest, processLLoyds, processLLoyds2, processHSBC, processBarclays, processHSBC_Scanned, processNatwest_Large_Scanned, processNatwest_Small_Scanned, processBarclays_Scanned
from flask import Response

def convert(file, filename):

    if filename == "Natwest":
        response = processNatwest(file, filename)
    elif filename == "LLoyds Bank":
        response = processLLoyds(file, filename)
    elif filename == "LLoyds Bank 2":
        response =  processLLoyds2(file, filename)
    elif filename == "HSBC":
        response = processHSBC(file, filename)
    elif filename == 'Barclays Bank':
        response = processBarclays(file, filename)
    elif filename == 'HSBC Scanned':
        response = processHSBC_Scanned(file, filename)
    elif filename == 'Natwest Large Scanned':
        response = processNatwest_Large_Scanned(file, filename)
    elif filename == 'Natwest Small Scanned':
        response = processNatwest_Small_Scanned(file, filename)
    elif filename == 'Barclays Bank Scanned':
        response = processBarclays_Scanned(file, filename)
    else:
        return Response(status=404)
    return response