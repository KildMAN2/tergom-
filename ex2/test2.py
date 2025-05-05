import csv
import os
import sys

FILENAME = "edge-profile.csv"

def check_file_exists_and_nonempty():
    if not os.path.exists(FILENAME):
        print("❌ File 'edge-profile.csv' not found.")
        return False
    if os.path.getsize(FILENAME) == 0:
        print("❌ File 'edge-profile.csv' is empty.")
        return False
    return True

def check_csv_format_and_stats():
    total_lines = 0
    malformed = 0
    taken_found = 0
    fallthrough_found = 0
    indirect_found = 0
    too_many_targets = 0

    try:
        with open(FILENAME, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                total_lines += 1

                if len(row) < 4:
                    malformed += 1
                    continue

                addr = row[0].strip()
                exec_count = row[1].strip()
                taken = row[2].strip()
                fall = row[3].strip()

                # Format checks
                if not addr.startswith("0x"):
                    malformed += 1
                    continue
                if not exec_count.isdigit():
                    malformed += 1
                    continue

                # Logic checks
                if taken.isdigit() and int(taken) > 0:
                    taken_found += 1
                if fall.isdigit() and int(fall) > 0:
                    fallthrough_found += 1

                # Indirect jumps check (targets start at index 4)
                target_count = (len(row) - 4) // 2
                if target_count > 0:
                    indirect_found += 1
                    if target_count > 10:
                        too_many_targets += 1

    except Exception as e:
        print(f"❌ Error reading the file: {e}")
        return False

    print(f"✅ Total lines (BBLs): {total_lines}")
    print(f"✅ Conditional branches with taken count: {taken_found}")
    print(f"✅ Conditional branches with fallthrough: {fallthrough_found}")
    print(f"✅ Indirect jump blocks: {indirect_found}")
    if too_many_targets > 0:
        print(f"❌ {too_many_targets} blocks have more than 10 indirect jump targets.")

    if total_lines < 500:
        print("❌ Too few BBLs for bzip2 (expected at least ~1000).")
        return False
    if malformed > 0:
        print(f"❌ {malformed} malformed rows detected.")
        return False

    print("✅ edge-profile.csv passed all structural checks.")
    return True

def main():
    print("🔍 Checking output of ex2.so on bzip2...")

    if not check_file_exists_and_nonempty():
        sys.exit(1)

    if not check_csv_format_and_stats():
        sys.exit(1)

    print("🎉 All checks passed. Your output looks good.")

if __name__ == "__main__":
    main()

