import os
from google import genai
import markdown
import pdfkit
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
from datetime import datetime

template_env = Environment(loader=FileSystemLoader("templates"))
template = template_env.get_template("report_template.html")

client = genai.Client(api_key="AIzaSyAkprftBkNPlq9Cu8OiaSpAkOtQW6tkpY8")

def make_prompt(analysis_result):
    ratios = analysis_result["ratios"]
    profits = analysis_result["profitability"]
    costs = analysis_result["cost_structure"]
    changes = analysis_result["large_changes"]

    if "error" in ratios:
        return "재무제표에서 필수 항목을 찾을 수 없어 분석을 완료하지 못했습니다."

    return f"""
당기 법인 재무제표 데이터를 바탕으로 전문 회계사 스타일로 작성된 분석 보고서를 생성해주세요.

### 분석 개요

- 본 보고서는 AI 분석 모델 Gemini 2.5 Pro를 통해 자동 생성되었습니다.

### 주요 재무비율

- 유동비율: {ratios.get("유동비율", "N/A")}%
- 부채비율: {ratios.get("부채비율", "N/A")}%

### 수익성 지표

{profits}

### 제조원가 구조

{costs}

### 전기 대비 30% 이상 증감 계정

{changes.to_markdown(index=False)}

### 결론 및 제언

- 수치에 대한 요약 해석
- 기준 이하/초과 항목에 대한 분석적 의견
- 제조원가와 수익성의 관계 분석
- 급격한 변동의 가능 원인에 대한 간략한 추정

문체는 전문 재무 보고서 스타일로 작성해주세요. 각 항목은 제목을 포함해 명확히 구분하고, 숫자는 반올림하여 간결하게 표현해주세요.
"""

def call_gemini(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-pro-exp-03-25",
        contents=prompt,
    )
    return response.text

def generate_report(analysis_result, company_name):
    prompt = make_prompt(analysis_result)
    print("[INFO] Gemini API 호출 중...")
    summary = call_gemini(prompt)

    # Markdown 저장 (기존 방식 유지)
    md_path = "재무분석보고서.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# 📊 {company_name} 재무제표 분석 보고서\n\n")
        f.write(f"> 작성일자: {datetime.today().strftime('%Y년 %m월 %d일')}\n")
        f.write("> 본 보고서는 Google Gemini 모델을 활용해 자동 생성되었습니다.\n\n")
        f.write(summary)
    print(f"[완료] 마크다운 보고서 생성: {md_path}")

    # PDF 저장용 HTML 생성
    sections = []
    for part in summary.split("###"):
        lines = part.strip().split("\n", 1)
        if len(lines) == 2:
            heading, content = lines
            sections.append({"heading": heading.strip(), "content": content.strip()})

    rendered_html = template.render(
        title=f"{company_name} 재무제표 분석 보고서",
        subtitle="AI 기반 자동 분석 보고서 (Gemini 2.5 Pro)",
        date=datetime.today().strftime("%Y년 %m월 %d일"),
        company=company_name,
        sections=sections
    )

    pdf_path = "재무분석보고서.pdf"
    pdfkit.from_string(rendered_html, pdf_path)
    print(f"[완료] PDF 보고서 생성: {pdf_path}")

