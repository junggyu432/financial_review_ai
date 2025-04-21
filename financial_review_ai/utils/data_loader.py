import pandas as pd
import re
import os

# 📁 기본 경로 설정
DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_sheet(file_name, data_dir):
    file_path = os.path.join(data_dir, file_name)
    return pd.read_excel(file_path, sheet_name=0, header=None, engine="xlrd", dtype=str)

def normalize_account_name(name):
    name = str(name)
    name = re.sub(r"\s+", "", name)           # 공백 제거
    name = re.sub(r"[^\w가-힣]", "", name)     # 특수문자 제거 (로마숫자, 점 등 포함)
    return name

def to_number(val):
    if pd.isnull(val):
        return 0
    val = str(val).strip()
    val = val.replace("−", "-")               # 유니코드 마이너스 처리
    val = re.sub(r"[^\d\-]", "", val)         # 숫자와 -만 남김
    return pd.to_numeric(val, errors="coerce")

def pick_value(row, col1, col2):
    v = to_number(row[col1])
    return v if v != 0 else to_number(row[col2])

# 📘 재무상태표 정제
def clean_balance_sheet(df_raw):
    df = df_raw.iloc[3:].copy()
    df.columns = ["계정과목", "당기_금", "당기_액", "전기_금", "전기_액"]
    df["계정과목"] = df["계정과목"].apply(normalize_account_name)

    df["당기금액"] = df.apply(lambda row: pick_value(row, "당기_금", "당기_액"), axis=1)
    df["전기금액"] = df.apply(lambda row: pick_value(row, "전기_금", "전기_액"), axis=1)

    return df[["계정과목", "당기금액", "전기금액"]].dropna(subset=["계정과목"])

# 📙 손익계산서 정제
def clean_pl_sheet(df_raw):
    df = df_raw.iloc[2:].copy()
    df.columns = ["계정과목", "당기_금1", "당기_금2", "전기_금1", "전기_금2"]
    df["계정과목"] = df["계정과목"].apply(normalize_account_name)

    df["당기금액"] = df.apply(lambda row: pick_value(row, "당기_금1", "당기_금2"), axis=1)
    df["전기금액"] = df.apply(lambda row: pick_value(row, "전기_금1", "전기_금2"), axis=1)

    return df[["계정과목", "당기금액", "전기금액"]].dropna(subset=["계정과목"])

# 📕 제조원가명세서 정제
def clean_msc_sheet(df_raw):
    df = df_raw.iloc[2:].copy()
    has_ratio = df.shape[1] >= 7 and df.iloc[:, 6].notna().any()

    if has_ratio:
        df.columns = ["계정과목", "당기_금1", "당기_금2", "당기_비율", "전기_금1", "전기_금2", "전기_비율"]
    else:
        df.columns = ["계정과목", "당기_금1", "당기_금2", "전기_금1", "전기_금2"]

    df["계정과목"] = df["계정과목"].apply(normalize_account_name)

    df["당기금액"] = df.apply(lambda row: pick_value(row, "당기_금1", "당기_금2"), axis=1)
    df["전기금액"] = df.apply(lambda row: pick_value(row, "전기_금1", "전기_금2"), axis=1)

    return df[["계정과목", "당기금액", "전기금액"]].dropna(subset=["계정과목"])

# 📦 전체 로딩 함수
def load_financial_data(data_dir=None):
    if data_dir is None:
        data_dir = DEFAULT_DATA_DIR
    
    bs_df = load_sheet("BS.xls", data_dir)
    pl_df = load_sheet("PL.xls", data_dir)
    msc_df = load_sheet("MSC.xls", data_dir)

    print("[INFO] 재무제표 데이터 로딩 및 정제 완료")
    return {
        "balance_sheet": clean_balance_sheet(bs_df),
        "income_statement": clean_pl_sheet(pl_df),
        "cost_sheet": clean_msc_sheet(msc_df),
    }
