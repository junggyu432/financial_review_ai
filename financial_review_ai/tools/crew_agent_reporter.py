from crewai import Agent
from crewai.tools import BaseTool
from financial_statement_analysis.utils.reporter import generate_report
from typing import Dict, Any

class GenerateReportTool(BaseTool):
    name: str = "generate_report"
    description: str = "분석 결과(dict)와 회사명을 받아 Markdown+PDF 보고서 생성"
    
    def _run(self, analysis: Dict[str, Any], company_name: str) -> str:
        generate_report(analysis_result=analysis, company_name=company_name)
        return "보고서 생성 완료"

report_tool = GenerateReportTool()

reporter_agent = Agent(
    role="보고서 작성자",
    goal="분석 결과를 기반으로 AI 스타일의 재무 보고서를 Markdown과 PDF로 작성",
    backstory="Gemini 모델을 활용해 자동으로 보고서를 작성하는 전문가",
    tools=[report_tool],
    verbose=True,
)
