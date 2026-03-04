from zeep import Client

WSDL_URL = "http://localhost:8003/?wsdl"

def main():
    client = Client(wsdl=WSDL_URL)

    # Test : 436 km, autonomie 450 km, 110 km/h, 25 min par recharge
    res = client.service.estimate_trip_time(436.0, 450.0, 110.0, 25)

    # res est un objet Zeep, mais print marche bien
    print("Réponse SOAP brute:", res)
    print("stops =", res.stops)
    print("drive_time_min =", res.drive_time_min)
    print("charge_time_min_total =", res.charge_time_min_total)
    print("total_time_min =", res.total_time_min)
    print("message =", res.message)

if __name__ == "__main__":
    main()