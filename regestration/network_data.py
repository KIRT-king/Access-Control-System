import requests
import uuid

def get_mac():
    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                            for ele in range(0, 8*6, 8)][::-1])
    return mac_address

def get_external_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()["ip"]
    except requests.RequestException as e:
        print("Не удалось получить внешний IP:", e)
        return None

def get_location(ip):
    try:
        response = requests.get(f'https://ipinfo.io/{ip}/json')
        data = response.json()
        location = str(data.get("country")) + "; " + str(data.get("city"))
        return location
    except Exception as e:
        print("Не удалось получить местоположение по IP:", e)
        return None, None, None, None