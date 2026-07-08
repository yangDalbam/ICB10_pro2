"""
한국관광공사 API 12개 지정 항목 데이터를 스케줄에 따라 수집하여 CSV로 저장하는 스크립트입니다.
주요 기능:
- 12개의 kto_api 함수를 순차적으로 호출하여 데이터 수집
- 수집된 데이터가 존재할 경우 data 폴더에 개별 저장 (파일명: YYYYMMDD_HHMMSS_[항목명].csv)
- 수집 결과를 요약 출력
"""

import os
from datetime import datetime
import pandas as pd
from api.kto_api import (
    get_foreign_visitor_region_ratio,
    get_foreign_visitor_activity,
    get_foreign_visitor_spend,
    get_related_tourist_spots,
    get_local_visitor_count,
    get_foreign_visitor_demographics,
    get_visitor_by_nationality,
    get_sns_and_navigation,
    get_search_by_tour_type,
    get_spend_type_by_country,
    get_spend_trend_by_industry,
    get_foreign_visitor_trend_by_region
)

# 수집 대상 항목과 해당 함수 매핑
TARGET_ITEMS = {
    "외래관광객지역비율": get_foreign_visitor_region_ratio,
    "외래관광객방한활동비율": get_foreign_visitor_activity,
    "외래관광객지출": get_foreign_visitor_spend,
    "연관관광지정보목록": get_related_tourist_spots,
    "지역방문자수집계": get_local_visitor_count,
    "방한외래관광객통계": get_foreign_visitor_demographics,
    "국적별방문자수_소비액": get_visitor_by_nationality,
    "SNS_내비게이션": get_sns_and_navigation,
    "유형별목적지검색량": get_search_by_tour_type,
    "국가별관광소비유형": get_spend_type_by_country,
    "업종별관광소비추이": get_spend_trend_by_industry,
    "외국인지역별방문자수추이": get_foreign_visitor_trend_by_region
}

def fetch_and_save():
    now = datetime.now()
    base_ym = now.strftime("%Y%m") # 현재 년월
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    
    print(f"[{timestamp}] 한국관광공사 12개 지정 항목 API 데이터 수집 시작 (기준연월: {base_ym})")
    
    # data 폴더 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    results = {}
    
    for name, func in TARGET_ITEMS.items():
        try:
            df = func(base_ym)
            
            if df is not None and not df.empty:
                filename = f"{timestamp}_{name}.csv"
                filepath = os.path.join(data_dir, filename)
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                results[name] = {"status": "성공", "message": f"저장 완료 ({len(df)}건)"}
                print(f" - [{name}] 수집 성공: {filepath}")
            else:
                results[name] = {"status": "빈값", "message": "데이터 없음 (API 미구현 또는 빈 결과)"}
                print(f" - [{name}] 수집 실패(빈 값 반환)")
                
        except Exception as e:
            results[name] = {"status": "오류", "message": str(e)}
            print(f" - [{name}] 수집 중 오류 발생: {e}")

    print("\n[수집 요약 보고]")
    for k, v in results.items():
        print(f" - {k}: {v['status']} ({v['message']})")
        
    return results

if __name__ == "__main__":
    fetch_and_save()
