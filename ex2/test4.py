import csv
import sys
import os
import subprocess
import time

EDGE_FILE = "edge-profile.csv"
PIN_PATH = os.path.expanduser("~/Documents/pin-3.30-98830-g1d7b601b3-gcc-linux/pin")
PIN_TOOL = "./ex2.so"
TARGET_BINARY = "./tst"
TARGET_ARGS = []

def run_pintool():
    print("⚙️ Running pintool...")
    if os.path.exists(EDGE_FILE):
        os.remove(EDGE_FILE)

    start = time.time()

    try:
        subprocess.run([PIN_PATH, "-t", PIN_TOOL, "--", TARGET_BINARY] + TARGET_ARGS, timeout=6)
    except subprocess.TimeoutExpired:
        print("❌ Pintool execution took too long (> 6 seconds).")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running pintool: {e}")
        sys.exit(1)

    runtime = time.time() - start
    print(f"✅ Pintool runtime: {runtime:.2f} seconds")

    if runtime > 5.0:
        print("❌ Pintool runtime exceeds 5 seconds limit.")
        sys.exit(1)

def validate_edge_profile():
    if not os.path.exists(EDGE_FILE):
        print("❌ edge-profile.csv not found.")
        sys.exit(1)

    with open(EDGE_FILE, newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    if not rows:
        print("❌ edge-profile.csv is empty.")
        sys.exit(1)

    total_lines = 0
    conditional_blocks = 0
    indirect_blocks = 0
    bad_rows = 0
    exec_counts = []
    bbl_addresses = set()

    for row in rows:
        total_lines += 1

        if len(row) < 4:
            bad_rows += 1
            continue

        addr = row[0].strip()
        exec_count = row[1].strip()
        taken = row[2].strip()
        fallthrough = row[3].strip()

        if not addr.startswith("0x") or not exec_count.isdigit():
            bad_rows += 1
            continue

        bbl_addresses.add(addr)
        exec_counts.append(int(exec_count))

        if taken.isdigit() and int(taken) > 0:
            conditional_blocks += 1
        if fallthrough.isdigit() and int(fallthrough) > 0:
            conditional_blocks += 1

        if len(row) > 4:
            # Indirect target format: alternating address,count pairs
            extra = row[4:]
            if len(extra) % 2 != 0:
                bad_rows += 1
                continue
            seen_targets = set()
            for i in range(0, len(extra), 2):
                tgt_addr = extra[i].strip()
                tgt_count = extra[i+1].strip()
                if not tgt_addr.startswith("0x") or not tgt_count.isdigit():
                    bad_rows += 1
                    break
                if tgt_addr in seen_targets:
                    print(f"⚠️ Duplicate indirect target {tgt_addr} in row {total_lines}")
                seen_targets.add(tgt_addr)
            indirect_blocks += 1

    print(f"✅ Total BBLs: {total_lines}")
    print(f"✅ Conditional branches detected: {conditional_blocks}")
    print(f"✅ Indirect jump blocks detected: {indirect_blocks}")
    print(f"⚙️ Malformed rows: {bad_rows}")

    if len(exec_counts) < 2:
        print("❌ Not enough valid BBL entries to validate sorting.")
        sys.exit(1)

    # Check if sorted descending by execCount
    if exec_counts != sorted(exec_counts, reverse=True):
        print("❌ BBLs are not sorted from hottest to coldest by execCount.")
        sys.exit(1)
    else:
        print("✅ BBLs are sorted correctly by execCount.")

    if total_lines < 100:
        print("❌ Too few BBLs detected — expected at least a few hundreds.")
        sys.exit(1)

    if conditional_blocks == 0:
        print("❌ No conditional branches detected — taken/fallthrough missing.")
        sys.exit(1)

    if bad_rows > 0:
        print("❌ Malformed rows detected — check your CSV formatting.")
        sys.exit(1)

    # Show top 5 hottest blocks
    print("\n🔥 Top 5 hottest BBLs (address and exec count):")
    with open(EDGE_FILE, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i >= 5: break
            print(f"  {row[0]} => {row[1]} execs")

    print("\n🎉 Output looks GOOD. READY TO SUBMIT!")

def main():
    run_pintool()
    validate_edge_profile()

if __name__ == "__main__":
    main()

