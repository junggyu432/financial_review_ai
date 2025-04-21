import logging
import argparse
from dotenv import load_dotenv
from crewai import Crew, Task
from financial_statement_analysis.settings import settings
from financial_statement_analysis.tools.crew_agent_loader import data_loader_agent
from financial_statement_analysis.tools.crew_agent_analyzer import analyzer_agent
from financial_statement_analysis.tools.crew_agent_reporter import reporter_agent

# 환경 변수 로드 및 키 확인
load_dotenv()
if not settings.gemini_api_key:
    raise RuntimeError("GEMINI_API_KEY가 설정되지 않았습니다. .env를 확인하세요.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def main():
    parser = argparse.ArgumentParser(description="법인 재무제표 자동 분석 (CrewAI)")
    parser.add_argument("--bs",  default="data/BS.xls", help="BS.xls 파일 경로 (기본: data/BS.xls)")
    parser.add_argument("--pl",  default="data/PL.xls", help="PL.xls 파일 경로 (기본: data/PL.xls)")
    parser.add_argument("--msc", default="data/MSC.xls", help="MSC.xls 파일 경로 (기본: data/MSC.xls)")
    parser.add_argument("--company-name", required=True, help="보고서에 사용할 회사명")
    parser.add_argument(
        "--threshold",
        type=float,
        default=settings.change_threshold,
        help=f"변동 탐지 임계치 (기본: {settings.change_threshold*100:.0f}%)"
    )
    args = parser.parse_args()
    print(f"[DEBUG] args.bs={args.bs}, args.pl={args.pl}, args.msc={args.msc}")

    task1 = Task(
        description="재무제표 로드 및 정제",
        expected_output="DataFrame dict",
        agent=data_loader_agent,
        inputs={
            "bs_path": args.bs,
            "pl_path": args.pl,
            "msc_path": args.msc,
        }
    )
    task2 = Task(
        description="재무 지표 분석",
        expected_output="분석 결과 dict",
        agent=analyzer_agent,
        inputs={"change_threshold": args.threshold}
    )
    task3 = Task(
        description="보고서 생성",
        expected_output="Markdown+PDF 보고서",
        agent=reporter_agent,
        inputs={"company_name": args.company_name}
    )

    crew = Crew(
        agents=[data_loader_agent, analyzer_agent, reporter_agent],
        tasks=[task1, task2, task3],
        verbose=True
    )

    try:
        crew.kickoff()
        logging.info("✅ 전체 분석 및 보고서 생성 완료")
    except Exception as e:
        logging.error(f"❌ 워크플로우 실행 중 오류 발생: {e}", exc_info=True)

if __name__ == "__main__":
    main()
