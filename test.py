def read_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    result = []
    for line in lines:
        parts = line.strip().split(',')
        if len(parts) != 6:
            continue
        image_name = parts[0].strip()
        rtn_name = parts[2].strip()
        try:
            instr_count = int(parts[4].strip())
            rtn_count = int(parts[5].strip())
        except ValueError:
            continue
        result.append((image_name, rtn_name, instr_count, rtn_count))
    # מיון מהכי הרבה הוראות לפחות, ואז לפי שם פונקציה
    return sorted(result, key=lambda x: (-x[2], x[1]))

try:
    actual = read_file("rtn-output.csv")
    expected = read_file("rtn-output-tst.csv")

    if actual == expected:
        print("✅ SUCCESS: The output is functionally correct.")
    else:
        print("❌ FAILURE: The output differs from the expected results.\n")
        diff_actual = set(actual) - set(expected)
        diff_expected = set(expected) - set(actual)

        if diff_actual:
            print("🔺 Lines in actual output but not expected:")
            for line in diff_actual:
                print("   ", line)

        if diff_expected:
            print("\n🔻 Lines expected but not found in actual output:")
            for line in diff_expected:
                print("   ", line)

except Exception as e:
    print(f"🔧 Error during verification: {e}")
