from crewai import Agent
from crewai.tools import BaseTool
from financial_statement_analysis.utils.data_loader import load_financial_data
from typing import Dict, Any


class LoadFinancialDataTool(BaseTool):
    name: str = "load_financial_data"
    description: str = "BS, PL, MSC 파일 경로를 받아 표준화된 DataFrame dict로 반환"

    def _run(
        self,
        bs_path: str,
        pl_path: str,
        msc_path: str
    ) -> Dict[str, Any]:
        print(f"[INFO] BS 파일 경로: {bs_path}")
        print(f"[INFO] PL 파일 경로: {pl_path}")
        print(f"[INFO] MSC 파일 경로: {msc_path}")

        return load_financial_data(bs_path, pl_path, msc_path)


load_data_tool = LoadFinancialDataTool()

data_loader_agent = Agent(
    role="재무제표 정제 담당자",
    goal="BS, PL, MSC 엑셀 파일을 읽어 정제된 DataFrame으로 변환",
    backstory="각 재무제표 파일을 자동으로 읽고 정제하여 분석에 적합한 구조로 만들어 주는 전문가",
    tools=[load_data_tool],
    verbose=True,
)
