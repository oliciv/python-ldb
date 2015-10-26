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
        s = []
        for service in data['services']:
            calling_points_str = ", ".join([p['locationName'] for p in service['calling_points']])
            s.append([service['destination_name'], service['std'], service['etd'], calling_points_str])
        tab_headers = ['Destination', 'STD', 'ETD', 'Calling at',]
        return tabulate(s, headers=tab_headers)

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
            this_service = {}
            _attributes = ['sta', 'eta', 'std', 'etd', 'platform', 'operator',
                           'operatorCode', 'serviceType', 'serviceID',]
            for attribute in _attributes:
                this_service[attribute] = getattr(service, attribute, None)
            this_service.update({
                 'origin_name': service.origin.location[0].locationName,
                 'origin_crs': service.origin.location[0].locationName,
                 'destination_name': service.destination.location[0].locationName,
                 'destination_crs': service.destination.location[0].locationName,
                })
            _calling_points = []
            for calling_point in getattr(service, 'subsequentCallingPoints')[0][0]['callingPoint']:
                _calling_points.append({'locationName': calling_point['locationName'],
                                        'crs': calling_point['crs'],
                                        'st': calling_point['st'],
                                        'et': calling_point['et']})
            this_service.update({'calling_points': _calling_points})
            _services.append(this_service)
        returned['services'] = _services
        return returned
