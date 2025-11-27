import requests
import pytest
import os

auth_data = {
        "UserName": "root",
        "Password": "0penBmc"
    }

def test_auth():
    print("\n\n\nТЕСТ АУНТИФИКАЦИИ")

    session = requests.Session()
    session.verify = False

    response = session.post(
        "https://localhost:2443/redfish/v1/SessionService/Sessions",
        json=auth_data
    )

    assert response.status_code == 201
    print(f"Сессия создана post код = 201")

    auth_token = response.headers.get('X-Auth-Token')
    assert auth_token is not None
    print(f"Токен получен  токен = {auth_token}")

    check_response = session.get("https://localhost:2443/redfish/v1/")
    assert check_response.status_code == 200
    print(f"get код = 200 после успешной аутентификации")


def test_info():
    print("\n\n\nТЕСТ ИНФОРМАЦИИ")

    session = requests.Session()
    session.verify = False
    session.auth =  (auth_data["UserName"],auth_data["Password"])



    response = session.get("https://localhost:2443/redfish/v1/Systems/system")
    assert response.status_code == 200
    print(f"Get-запрос прошёл успешно код = 200")

    check_json = response.json()
    assert  "Status" in check_json
    assert  "PowerState" in check_json
    print(f"Status и PowerState - есть в json")
    print(f"Status = {check_json["Status"]} PowerState = {check_json["PowerState"]}")


def test_power():
    print("\n\n\nТЕСТ ПИТАНИЯ")

    session = requests.Session()
    session.verify = False
    session.auth = (auth_data["UserName"], auth_data["Password"])

    response = session.post(
        f"https://localhost:2443/redfish/v1/Systems/system/Actions/ComputerSystem.Reset",
        json={"ResetType": "On"  })

    assert response.status_code == 202

    status_response = session.get("https://localhost:2443/redfish/v1/Systems/system")
    assert status_response.json().get("PowerState") == "On"


def test_temp():
    print("\n\n\nТЕСТ ТЕМПЕРАТУРЫ")

    session = requests.Session()
    session.verify = False
    session.auth = (auth_data["UserName"], auth_data["Password"])

    response = session.get("https://localhost:2443/redfish/v1/Systems/system/Processors")
    assert response.status_code == 200

    temp_data = response.json()
    temp_members = temp_data.get('Members', [])
    assert len(temp_members) > 0

    print(temp_data)


def test_IPMI():
    print("\n\n\nТЕСТ IPMI")

    session = requests.Session()
    session.verify = False
    session.auth = (auth_data["UserName"], auth_data["Password"])
    response_redfish = session.get("https://localhost:2443/redfish/v1/Systems/system/Processors")
    redfish_json = response_redfish.json()
    print(f"Redfish датчики: {redfish_json}")

    assert response_redfish.status_code == 200

    temp_data = response_redfish.json()
    temp_members = temp_data.get('Members', [])
    assert len(temp_members) > 0

    cmd = 'ipmitool -I lanplus -H localhost -U root -P 0penBmc -p 2623 sensor list'
    with os.popen(cmd) as process:
        output = process.read()

    print(output)
