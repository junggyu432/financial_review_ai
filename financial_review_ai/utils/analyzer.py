import pandas as pd
import re

KEY_ITEMS = {
    "유동자산": "유동자산",
    "유동부채": "유동부채",
    "총부채": "부채총계",
    "총자본": "자본총계",
    "매출액": "매출액",
    "매출총이익": "매출총이익",
    "영업이익": "영업이익",
    "당기순이익": "당기순이익",
    "당기총제조비용": "당기총제조비용",
    "당기제품제조원가": "당기제품제조원가",
    "감가상각비": "감가상각비",
    "인건비": ["임금","급여","상여금","직원급여","임원급여","잡급"],
}

def normalize_account_name(name):
    name = str(name)
    name = re.sub(r"\s+", "", name)          # 모든 공백 제거
    name = re.sub(r"[^\w가-힣]", "", name)    # 특수문자 제거 (로마 숫자, 점 등 포함)
    return name

def find_value(df, keywords, value_col="당기금액"):
    df["계정과목"] = df["계정과목"].apply(normalize_account_name)
    for keyword in keywords if isinstance(keywords, list) else [keywords]:
        row = df[df["계정과목"].str.contains(keyword)]
        if not row.empty:
            return row.iloc[0][value_col]
    return 0

def calculate_ratios(bs_df):
    try:
        유동자산 = find_value(bs_df, KEY_ITEMS["유동자산"])
        유동부채 = find_value(bs_df, KEY_ITEMS["유동부채"])
        총부채 = find_value(bs_df, KEY_ITEMS["총부채"])
        총자본 = find_value(bs_df, KEY_ITEMS["총자본"])

        print(f"[DEBUG] 유동자산: {유동자산}, 유동부채: {유동부채}, 총부채: {총부채}, 총자본: {총자본}")

        유동비율 = (유동자산 / 유동부채) * 100 if 유동부채 else None
        부채비율 = (총부채 / 총자본) * 100 if 총자본 else None

        return {
            "유동비율": round(유동비율, 2) if 유동비율 is not None else None,
            "부채비율": round(부채비율, 2) if 부채비율 is not None else None,
        }
    except Exception as e:
        return {"error": str(e)}

def calculate_profitability(pl_df):
    result = {}
    for key in ["매출액", "매출총이익", "영업이익", "당기순이익"]:
        result[key] = find_value(pl_df, KEY_ITEMS[key])
    return result

def summarize_cost_structure(msc_df):
    result = {}
    for key in ["당기총제조비용", "당기제품제조원가", "감가상각비", "인건비"]:
        result[key] = find_value(msc_df, KEY_ITEMS[key])
    return result

def detect_large_changes(df, threshold=0.3):
    df = df.copy()
    df["변화율"] = abs(df["당기금액"] - df["전기금액"]) / df["전기금액"].replace(0, pd.NA)
    return df[df["변화율"] >= threshold].sort_values("변화율", ascending=False)

def analyze_ratios_and_changes(data_dict, threshold=0.3):
    bs_df = data_dict["balance_sheet"]
    pl_df = data_dict["income_statement"]
    msc_df = data_dict["cost_sheet"]

    return {
        "ratios": calculate_ratios(bs_df),
        "profitability": calculate_profitability(pl_df),
        "cost_structure": summarize_cost_structure(msc_df),
        "large_changes": detect_large_changes(pd.concat([bs_df, pl_df, msc_df]), threshold),
    }
