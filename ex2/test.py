import csv
import sys

EXPECTED_CALLS = 4000
EXPECTED_LOOP_MIN_EXECUTIONS = 4000

def validate_edge_profile(filename):
    try:
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
    except FileNotFoundError:
        print(f"❌ File '{filename}' not found.")
        sys.exit(1)

    if not rows:
        print("❌ File is empty.")
        sys.exit(1)

    call_blocks = 0
    loop_blocks = 0

    for row in rows:
        if len(row) < 4:
            print(f"❌ Invalid row format: {row}")
            sys.exit(1)

        addr = row[0].strip()
        exec_count = int(row[1].strip())
        taken_count = int(row[2].strip())
        fallthrough_count = int(row[3].strip())

        # Check for calls
        if exec_count == EXPECTED_CALLS:
            call_blocks += 1

        # Check for loops
        if taken_count > 0 or fallthrough_count > 0:
            loop_blocks += 1

    print(f"Found {call_blocks} function call blocks with {EXPECTED_CALLS} executions.")
    print(f"Found {loop_blocks} loop blocks (conditional branches).")

    if call_blocks >= 3:
        print("✅ Function call counts look correct (gal, bar, foo).")
    else:
        print("❌ Function call counts mismatch.")
        sys.exit(1)

    if loop_blocks >= 2:
        print("✅ Loop blocks detected correctly.")
    else:
        print("❌ Loop block detection failed.")
        sys.exit(1)

    print("✅ Validation passed.")

if __name__ == "__main__":
    validate_edge_profile('edge-profile.csv')

