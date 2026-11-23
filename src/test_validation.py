
import pandas as pd
from performance_model import validate_data


# Valid sample attendee record
VALID_DATA = {
    "attendee_id": ["CCI001"],
    "attendee_name": ["John"],
    "category": ["Student"],
    "attendance_rate": [100],
    "session_participation": [9],
    "practical_engagement": [9],
    "teamwork": [8],
    "activities_completed": [90],
    "feedback_score": [9]
}


def run_test(test_name, test_data, should_pass):
    print(f"\nTesting: {test_name}")

    try:
        validate_data(test_data)

        if should_pass:
            print("PASS: Valid data was accepted.")
            return True
        else:
            print("FAIL: Invalid data was accepted.")
            return False

    except (ValueError, TypeError) as error:
        if not should_pass:
            print("PASS: Invalid data was rejected.")
            print(error)
            return True
        else:
            print("FAIL: Valid data was rejected.")
            print(error)
            return False


def main():
    results = []

    # Test 1: Valid attendee record
    test_data = pd.DataFrame(VALID_DATA)
    results.append(
        run_test("Valid attendee record", test_data, True)
    )

    # Test 2: Missing attendee name
    test_data = pd.DataFrame(VALID_DATA)
    test_data.loc[0, "attendee_name"] = ""
    results.append(
        run_test("Missing attendee name", test_data, False)
    )

    # Test 3: Duplicate attendee ID
    test_data = pd.DataFrame([
        {key: value[0] for key, value in VALID_DATA.items()},
        {key: value[0] for key, value in VALID_DATA.items()}
    ])

    results.append(
        run_test("Duplicate attendee ID", test_data, False)
    )

    # Test 4: Invalid attendee category
    test_data = pd.DataFrame(VALID_DATA)
    test_data.loc[0, "category"] = "Teacher"
    results.append(
        run_test("Invalid attendee category", test_data, False)
    )

    # Test 5: Attendance rate above 100
    test_data = pd.DataFrame(VALID_DATA)
    test_data.loc[0, "attendance_rate"] = 120
    results.append(
        run_test("Attendance rate above 100", test_data, False)
    )

    # Test 6: Session participation above 10
    test_data = pd.DataFrame(VALID_DATA)
    test_data.loc[0, "session_participation"] = 15
    results.append(
        run_test("Session participation above 10", test_data, False)
    )

    # Test 7: Non-numeric feedback score
    test_data = pd.DataFrame(VALID_DATA)
    test_data["feedback_score"] = (
        test_data["feedback_score"].astype("object")
    )
    test_data.loc[0, "feedback_score"] = "Excellent"
    results.append(
        run_test("Non-numeric feedback score", test_data, False)
    )

    # Test 8: Missing required column
    test_data = pd.DataFrame(VALID_DATA)
    test_data = test_data.drop(columns=["attendee_name"])
    results.append(
        run_test("Missing required column", test_data, False)
    )

    # Test 9: Lowercase category normalization
    test_data = pd.DataFrame(VALID_DATA)
    test_data.loc[0, "category"] = "student"
    results.append(
        run_test("Lowercase category normalization", test_data, True)
    )

    # Test 10: Empty dataset
    test_data = pd.DataFrame(columns=VALID_DATA.keys())
    results.append(
        run_test("Empty dataset", test_data, False)
    )

    # Display test summary
    total_tests = len(results)
    passed_tests = sum(results)
    failed_tests = total_tests - passed_tests

    print("\n" + "=" * 45)
    print("CCI STEM CONNECT DATA VALIDATION TEST SUMMARY")
    print("=" * 45)

    print(f"Total tests: {total_tests}")
    print(f"Passed tests: {passed_tests}")
    print(f"Failed tests: {failed_tests}")

    if failed_tests == 0:
        print("\nAll validation tests passed successfully!")
    else:
        print("\nSome tests failed. Please review the results.")


if __name__ == "__main__":
    main()
