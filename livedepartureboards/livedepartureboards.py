from suds.client import Client
from tabulate import tabulate


class DepartureBoard:
    """
    Contains information about a single departure board
    """

    def __init__(self, token):
        self.token = token

    def tabulate_all(self, crs_code):
        """
        Generate a tabulated list of all services calling at this station
        """
        data = self.get_data(crs_code)
        s = [[service['destination_name'], service['std'], service['etd']] for service in data['services']]
        tab_headers = ['Destination', 'STD', 'ETD']
        print tabulate(s, headers=tab_headers)

    def get_data(self, crs_code):
        """
        Get departure and arrival information from National Rail
        """
        client = Client('https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2015-05-14')
        token = client.factory.create("ns2:AccessToken")
        token.TokenValue = self.token
        client.set_options(soapheaders=(token,))
        station_info = client.service.GetDepBoardWithDetails(numRows=10, crs=crs_code)
        returned = {
            'name': station_info.locationName,
            'crs': station_info.crs,
        }
        if hasattr(station_info, 'nrccMessages'):
            returned['messages'] = station_info.nrccMessages
        else:
            returned['messages'] = None
        _services = []
        for service in station_info.trainServices.service:
            this_service = (
                {
                 'sta': getattr(service, 'sta', None),
                 'eta': getattr(service, 'eta', None),
                 'std': getattr(service, 'std', None),
                 'etd': getattr(service, 'etd', None),
                 'platform': service.platform,
                 'operator': service.operator,
                 'operatorCode': service.operatorCode,
                 'serviceType': service.serviceType,
                 'serviceID': service.serviceID,
                 'origin_name': service.origin.location[0].locationName,
                 'origin_crs': service.origin.location[0].locationName,
                 'destination_name': service.destination.location[0].locationName,
                 'destination_crs': service.destination.location[0].locationName,
                }

            )
            _services.append(this_service)
        returned['services'] = _services
        return returned
