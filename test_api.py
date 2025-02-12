import requests
import json

# آدرس‌های API
LOGIN_URL = "https://bi.kiagostar.com/api/api/login"
MERCHANDISE_URL = "https://bi.kiagostar.com/api/api/merchandise"

# اطلاعات کاربری
USERNAME = "api@kiagostar.com"
PASSWORD = "Api&&666525@@09"
MERCHANDISE_ID = 1011900027  # شماره محصول مورد نظر

def get_merchandise_info(username, password, merchandise_id):
    try:
        print("\n🔵 [STEP 1] Sending login request...")
        login_data = {"Username": username, "Password": password}
        login_response = requests.post(LOGIN_URL, json=login_data)

        if login_response.status_code != 200:
            print("❌ Login failed:", login_response.text)
            return

        token = login_response.json().get('token')
        if not token:
            print("❌ Token not found in response!")
            return

        print("✅ Login successful! Token received.")

        # مرحله 2: دریافت اطلاعات محصول
        print("\n🔵 [STEP 2] Fetching merchandise info...")
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive'
        }
        params = {'merchandiseId': merchandise_id}

        session = requests.Session()  # 👈 ایجاد سشن برای حفظ لاگین
        merchandise_response = session.get(MERCHANDISE_URL, headers=headers, params=params)

        print("🔹 Merchandise Response Code:", merchandise_response.status_code)
        print("🔹 Merchandise Headers:", merchandise_response.headers)
        print("🔹 Merchandise Raw Response:", merchandise_response.text[:500])  # فقط 500 کاراکتر اول چاپ شود

        if merchandise_response.status_code == 200:
            try:
                data = merchandise_response.json()
                print("✅ Merchandise info received:", json.dumps(data, indent=4, ensure_ascii=False))
            except json.JSONDecodeError as e:
                print("❌ JSON Decode Error:", str(e))
        else:
            print(f"❌ Failed to fetch merchandise info! Status Code: {merchandise_response.status_code}")
            print("🔹 Response Text:", merchandise_response.text)

    except requests.RequestException as e:
        print("❌ [ERROR] Network or API Request Error:", str(e))

if __name__ == "__main__":
    get_merchandise_info(USERNAME, PASSWORD, MERCHANDISE_ID)
