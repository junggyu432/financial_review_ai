from crewai import Agent
from crewai.tools import BaseTool
from financial_statement_analysis.utils.analyzer import analyze_ratios_and_changes
from typing import Dict, Any

class AnalyzeFinancialsTool(BaseTool):
    name: str = "analyze_financials"
    description: str = "정제된 재무 데이터(dict)와 임계치를 받아 주요 재무비율 및 변동 계정 분석"
    
    def _run(self, data: Dict[str, Any], change_threshold: float) -> Dict[str, Any]:
        return analyze_ratios_and_changes(data, threshold=change_threshold)

analyze_tool = AnalyzeFinancialsTool()

analyzer_agent = Agent(
    role="재무 분석가",
    goal="재무 데이터로부터 유동비율, 부채비율, 수익성, 제조원가 구조, 대변동 계정 탐지",
    backstory="기업의 재무 상태를 수치로 해석하는 AI 분석 전문가",
    tools=[analyze_tool],
    verbose=True,
)