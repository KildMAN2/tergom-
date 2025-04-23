import pandas as pd

def clean_df(df):
    # שמירה רק על העמודות שהשוואה תלויות בהן
    df.columns = ["ImageName", "ImageAddr", "RTNName", "RTNAddr", "InstructionCount", "RtnCount"]
    return df[["ImageName", "RTNName", "InstructionCount", "RtnCount"]].sort_values(by=["InstructionCount", "RTNName"], ascending=[False, True]).reset_index(drop=True)

try:
    df_actual = pd.read_csv("rtn-output.csv", header=None)
    df_expected = pd.read_csv("rtn-output-tst.csv", header=None)

    df_actual_clean = clean_df(df_actual)
    df_expected_clean = clean_df(df_expected)

    if df_actual_clean.equals(df_expected_clean):
        print("✅ SUCCESS: The output is functionally correct.")
    else:
        print("❌ FAILURE: The output differs from the expected results.")
        print("\nDifferences:")
        diff = pd.concat([df_actual_clean, df_expected_clean]).drop_duplicates(keep=False)
        print(diff.to_string(index=False))

except Exception as e:
    print(f"Error during verification: {e}")
