from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# 1. Test case-insensitivity (lowercase fields)
print("Testing case-insensitivity on POST /chat:")
try:
    response = client.post("/chat", json={"student_id": "JIS/2025/0262", "message": "hello"})
    print("Status code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Error:", e)

# 2. Test very long message on POST /chat
print("\nTesting very long message on POST /chat:")
try:
    response = client.post("/chat", json={"student_id": "JIS/2025/0262", "message": "A" * 100000})
    print("Status code:", response.status_code)
    print("Response JSON (partial bot_response):", response.json().get("bot_response")[:100])
except Exception as e:
    print("Error:", e)

# 3. Test raw JSON with unescaped raw newlines (replicates Swagger pasting issue)
print("\nTesting raw JSON with unescaped raw newlines:")
try:
    raw_json = '{\n  "student_id": "JIS/2025/0262",\n  "message": "is Intel Pentium processor capable to handle any Mac OS?\n\nNo, Apple has never natively supported Intel Pentium processors."\n}'
    response = client.post("/chat", headers={"content-type": "application/json"}, content=raw_json)
    print("Status code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Error:", e)

# 4. Test slash routing on GET /chat/history/{student_id:path}
print("\nTesting slash routing on GET /chat/history:")
try:
    response = client.get("/chat/history/JIS/2025/0262")
    print("Status code:", response.status_code)
    print("Number of history entries:", len(response.json()))
except Exception as e:
    print("Error:", e)
