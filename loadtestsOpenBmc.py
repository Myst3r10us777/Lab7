from locust import HttpUser, between, task

auth_data = {
    "UserName": "root",
    "Password": "0penBmc"
}

class OpenBMCTestUser(HttpUser):
    host = "https://localhost:2443"

    @task(1)
    def test_openBMC(self):
        print("\n\n\nТЕСТ OpenBMC")

        self.client.verify = False
        self.client.auth = (auth_data["UserName"], auth_data["Password"])
        with self.client.get("/redfish/v1/Systems/system", catch_response=True, name="OpenBMC") as response:
            if response.status_code == 200:
                print(f"код запроса: {response}")
                response.success()
                power_data = response.json()
                print(f"PowerState: {power_data['PowerState']}")
            else:
                response.failure(f"Expected 200, got {response.status_code}")

class JSONPlaceholderTestUser(HttpUser):
    host = "https://jsonplaceholder.typicode.com"

    @task(1)
    def test_JSONPlaceholder(self):
        print("\n\n\nТЕСТ JSONPlaceholder")

        with self.client.get("/posts", catch_response=True, name="JSONPlaceholder") as response:
            if response.status_code == 200:
                print(f"код запроса: {response}")
                response.success()
                posts_data = response.json()
                print(f"Количество постов: {len(posts_data)}")
                if posts_data:
                    print(f"Первый пост: {posts_data[0]['title'][:50]}...")
            else:
                response.failure(f"Expected 200, got {response.status_code}")

class WttrTestUser(HttpUser):
    host = "https://wttr.in"

    @task(1)
    def test_wttr(self):
        print("\n\n\nТЕСТ Wttr")

        with self.client.get("/Novosibirsk?format=j1", catch_response=True, name="Wttr") as response:
            if response.status_code == 200:
                print(f"код запроса: {response}")
                response.success()
                weather_data = response.json()
                print(f"Температура: {weather_data['current_condition'][0]['temp_C']}°C")
                print(f"Погода: {weather_data['current_condition'][0]['weatherDesc'][0]['value']}")
            else:
                response.failure(f"Expected 200, got {response.status_code}")