import requests
import json
import time
import uuid

API_URL = "http://127.0.0.1:8000/ai/analyze-case" # Adjusted to match main.py route if applicable, or leave as /analyze-case


# =========================
# HELPER FUNCTIONS
# =========================

def print_divider():
    print("=" * 60)


def generate_customer_id():
    return f"CUST-{uuid.uuid4().hex[:6].upper()}"


def add_customer_id(payload):
    # Only auto-generate if the test isn't intentionally leaving it blank
    if "customer_id" not in payload:
        payload["customer_id"] = generate_customer_id()
    return payload


# 🔹 SUCCESS RESPONSE VALIDATION
def validate_success_response(data):
    required_fields = [
        "suggested_resolution",
        "similar_cases",
        "confidence_score",
        "explanation"
    ]

    # Check fields exist
    for field in required_fields:
        if field not in data:
            return False, f"Missing field: {field}"

    # Type checks
    if not isinstance(data["similar_cases"], list):
        return False, "similar_cases should be a list"

    if not (0.0 <= data["confidence_score"] <= 1.0):
        return False, "confidence_score out of range"

    if not isinstance(data["suggested_resolution"], str):
        return False, "suggested_resolution should be a string"

    return True, "Valid response structure"


# 🔹 ERROR RESPONSE VALIDATION
def validate_error_response(data):
    if "detail" not in data:
        return False, "Missing 'detail' in error response"
    return True, "Valid error response"


def send_request(payload, test_name, expected_status):
    print_divider()
    print(f"TEST: {test_name}")

    payload = add_customer_id(payload)

    start_time = time.time()

    try:
        response = requests.post(API_URL, json=payload)
        response_time = round((time.time() - start_time) * 1000, 2)

        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time} ms")

        try:
            data = response.json()
            print("Response JSON:")
            print(json.dumps(data, indent=4))
        except Exception:
            print("FAIL: Invalid JSON response")
            return False

        # 🔹 STATUS CHECK
        if response.status_code != expected_status:
            print(f"FAIL: Expected {expected_status}, got {response.status_code}")
            return False

        # 🔹 SUCCESS VALIDATION
        if response.status_code == 200:
            is_valid, message = validate_success_response(data)
            if not is_valid:
                print(f"FAIL: {message}")
                return False

        # 🔹 ERROR VALIDATION
        else:
            is_valid, message = validate_error_response(data)
            if not is_valid:
                print(f"FAIL: {message}")
                return False

        print("PASS")
        return True

    except Exception as e:
        print(f"ERROR: Request failed -> {e}")
        return False


# =========================
# TEST CASES
# =========================

test_cases = [

    # VALID CASE
    {
        "name": "Valid CCMS Case",
        "payload": {
            "case_description": "The login portal crashes every time I try to reset my password.",
            "location": "New York",
            "category": "Technical Issue"
        },
        "expected_status": 200
    },

    # EMPTY CASE DESCRIPTION
    {
        "name": "Empty Case Description",
        "payload": {
            "case_description": "   ",
            "location": "Chicago",
            "category": "Billing"
        },
        "expected_status": 422
    },

    # MISSING DESCRIPTION FIELD
    {
        "name": "Missing Description Field",
        "payload": {
            "location": "Dallas",
            "category": "General Inquiry"
        },
        "expected_status": 422
    },

    # MISSING CUSTOMER ID
    {
        "name": "Missing Customer ID",
        "payload": {
            "customer_id": "",
            "case_description": "My delivery was late by 3 days.",
            "location": "Seattle"
        },
        "expected_status": 422
    },

    # LONG INPUT
    {
        "name": "Long Case Description",
        "payload": {
            "case_description": "I have been trying to reach support for hours. " * 50,
            "location": "Boston",
            "category": "Customer Support"
        },
        "expected_status": 200
    },

    # MINIMAL VALID INPUT (Only required fields)
    {
        "name": "Minimal Valid Input",
        "payload": {
            "case_description": "Refund not processed."
        },
        "expected_status": 200
    }
]


# =========================
# MAIN EXECUTION
# =========================

if __name__ == "__main__":
    print("\nStarting CCMS Integration Simulation...\n")

    passed = 0
    failed = 0

    results_summary = []

    for test in test_cases:
        result = send_request(
            payload=test["payload"],
            test_name=test["name"],
            expected_status=test["expected_status"]
        )

        if result:
            passed += 1
            results_summary.append({"test": test["name"], "status": "PASS"})
        else:
            failed += 1
            results_summary.append({"test": test["name"], "status": "FAIL"})

    print_divider()
    print("FINAL SUMMARY")
    print(f"Total Tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    # SAVE RESULTS
    with open("test_results.json", "w") as f:
        json.dump(results_summary, f, indent=4)

    print("\nResults saved to test_results.json")
    print("CCMS Simulation Completed!")