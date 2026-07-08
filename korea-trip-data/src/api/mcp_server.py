"""
한국관광공사 API를 위한 MCP(Model Context Protocol) 서버 모듈입니다.
주요 기능:
- FastMCP를 사용하여 KTO API를 외부(에이전트 등)에서 도구(Tool)로 호출할 수 있도록 제공
- 신규 추가된 12개 수집 항목을 외부에서 호출 가능하게 구성
"""

from mcp.server.fastmcp import FastMCP
import pandas as pd
import json

# 기존 모듈에서 함수 임포트
from api.kto_api import (
    get_area_visitor_diversity,
    get_area_spend_diversity,
    get_area_intl_diversity,
    get_area_service_demand,
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

# FastMCP 서버 인스턴스 생성
mcp = FastMCP("kto-api-server", dependencies=["pandas", "requests", "python-dotenv"])

# ---------------------------------------------
# 기존 함수 기반 Tool
# ---------------------------------------------
@mcp.tool()
def fetch_kto_visitor_diversity(base_ym: str) -> str:
    df = get_area_visitor_diversity(base_ym)
    return df.to_json(orient='records', force_ascii=False) if not df.empty else "[]"

@mcp.tool()
def fetch_kto_spend_diversity(base_ym: str) -> str:
    df = get_area_spend_diversity(base_ym)
    return df.to_json(orient='records', force_ascii=False) if not df.empty else "[]"

@mcp.tool()
def fetch_kto_intl_diversity(base_ym: str) -> str:
    df = get_area_intl_diversity(base_ym)
    return df.to_json(orient='records', force_ascii=False) if not df.empty else "[]"

@mcp.tool()
def fetch_kto_service_demand(base_ym: str) -> str:
    df = get_area_service_demand(base_ym)
    return df.to_json(orient='records', force_ascii=False) if not df.empty else "[]"

# ---------------------------------------------
# 신규 12개 항목 기반 Tool
# ---------------------------------------------
@mcp.tool()
def fetch_foreign_visitor_region_ratio(base_ym: str) -> str:
    df = get_foreign_visitor_region_ratio(base_ym)
    return df.to_json(orient='records', force_ascii=False) if not df.empty else "[]"

@mcp.tool()
def fetch_foreign_visitor_activity(base_ym: str) -> str:
    df = get_foreign_visitor_activity(base_ym)
    return df.to_json(orient='records', force_ascii=False) if not df.empty else "[]"

@mcp.tool()
def fetch_foreign_visitor_spend(base_ym: str) -> str:
    df = get_foreign_visitor_spend(base_ym)
    return df.to_json(orient='records', force_ascii=False) if not df.empty else "[]"

@mcp.tool()
def fetch_related_tourist_spots(base_ym: str) -> str:
    df = get_related_tourist_spots(base_ym)
    return df.to_json(orient='records', force_ascii=False) if not df.empty else "[]"

@mcp.tool()
def fetch_local_visitor_count(base_ym: str) -> str:
    df = get_local_visitor_count(base_ym)
    return df.to_json(orient='records', force_ascii=False) if not df.empty else "[]"

@mcp.tool()
def fetch_foreign_visitor_demographics(base_ym: str) -> str:
    df = get_foreign_visitor_demographics(base_ym)
    return df.to_json(orient='records', force_ascii=False) if not df.empty else "[]"

@mcp.tool()
def fetch_visitor_by_nationality(base_ym: str) -> str:
    df = get_visitor_by_nationality(base_ym)
    return df.to_json(orient='records', force_ascii=False) if not df.empty else "[]"

@mcp.tool()
def fetch_sns_and_navigation(base_ym: str) -> str:
    df = get_sns_and_navigation(base_ym)
    return df.to_json(orient='records', force_ascii=False) if not df.empty else "[]"

@mcp.tool()
def fetch_search_by_tour_type(base_ym: str) -> str:
    df = get_search_by_tour_type(base_ym)
    return df.to_json(orient='records', force_ascii=False) if not df.empty else "[]"

@mcp.tool()
def fetch_spend_type_by_country(base_ym: str) -> str:
    df = get_spend_type_by_country(base_ym)
    return df.to_json(orient='records', force_ascii=False) if not df.empty else "[]"

@mcp.tool()
def fetch_spend_trend_by_industry(base_ym: str) -> str:
    df = get_spend_trend_by_industry(base_ym)
    return df.to_json(orient='records', force_ascii=False) if not df.empty else "[]"

@mcp.tool()
def fetch_foreign_visitor_trend_by_region(base_ym: str) -> str:
    df = get_foreign_visitor_trend_by_region(base_ym)
    return df.to_json(orient='records', force_ascii=False) if not df.empty else "[]"

if __name__ == "__main__":
    mcp.run()
