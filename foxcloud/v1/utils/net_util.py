import ipaddress

from foxcloud import exceptions as fox_exc


def validate_network(cidr):
    try:
        network = ipaddress.ip_network(cidr)
        return True if network else False
    except Exception as e:
        raise fox_exc.FoxCloudException(e)


def validate_ip_address(ip_address):
    try:
        ip = ipaddress.ip_address(ip_address)
        return True if ip else False
    except Exception as e:
        raise fox_exc.FoxCloudException(e)