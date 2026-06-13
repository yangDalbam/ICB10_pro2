"""
Streamlit 대시보드를 단일 HTML 파일로 변환 및 패키징하는 빌드 스크립트입니다.
stlite(Pyodide 기반 Streamlit) 기술을 활용하여 별도의 파이썬 서버 구동 없이 
웹 브라우저에서 독립적으로 동작하는 HTML 파일을 생성합니다.
"""

import os
import json

def build():
    # 빌드 스크립트 위치 기준 경로 설정
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, "src")
    
    # 패키징할 가상 파일 매핑 정의 (가상 경로, 실제 경로)
    files_to_collect = [
        ("app.py", os.path.join(src_dir, "app.py")),
        ("styles.py", os.path.join(src_dir, "styles.py")),
        ("api/__init__.py", os.path.join(src_dir, "api", "__init__.py")),
        ("api/odcloud_api.py", os.path.join(src_dir, "api", "odcloud_api.py")),
        ("api/kto_api.py", os.path.join(src_dir, "api", "kto_api.py")),
        ("pages/1_Foreigner_Trend.py", os.path.join(src_dir, "pages", "1_Foreigner_Trend.py")),
        ("pages/2_Tourism_Diversity.py", os.path.join(src_dir, "pages", "2_Tourism_Diversity.py")),
        ("pages/3_Demand_Analysis.py", os.path.join(src_dir, "pages", "3_Demand_Analysis.py")),
    ]
    
    files_dict = {}
    
    # 각 파이썬 파일 수집
    for virtual_path, real_path in files_to_collect:
        if os.path.exists(real_path):
            with open(real_path, "r", encoding="utf-8") as f:
                files_dict[virtual_path] = f.read()
        else:
            print(f"[Warning] 파일을 찾을 수 없습니다: {real_path}")
            if "api/__init__.py" in virtual_path:
                files_dict[virtual_path] = ""

    # Pyodide 내에서 python-dotenv 임포트 에러를 방지하기 위해 빈 .env 파일 추가 마운트
    files_dict[".env"] = "ODCLOUD_API_KEY=\nKTO_API_KEY=\n"

    # JSON 데이터 직렬화
    files_json = json.dumps(files_dict, ensure_ascii=False)
    
    # stlite mountable HTML 템플릿 작성
    html_content = f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta
      name="viewport"
      content="width=device-width, initial-scale=1, shrink-to-fit=no"
    />
    <title>Korea Trip Data랩 - 관광 대시보드 (오프라인/정적 실행 버전)</title>
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/@stlite/mountable@0.59.0/build/style.css"
    />
    <style>
      /* 로딩 spinner 디자인 */
      #spinner-container {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: #f7f9fa;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      }}
      .spinner {{
        border: 4px solid rgba(0, 0, 0, 0.1);
        width: 50px;
        height: 50px;
        border-radius: 50%;
        border-left-color: #00c73c;
        animation: spin 1s linear infinite;
        margin-bottom: 20px;
      }}
      @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
      }}
      .loading-text {{
        font-size: 1.1rem;
        color: #333;
        font-weight: 600;
      }}
      .sub-text {{
        font-size: 0.85rem;
        color: #666;
        margin-top: 8px;
      }}
    </style>
  </head>
  <body>
    <div id="spinner-container">
      <div class="spinner"></div>
      <div class="loading-text">Korea Trip Data랩 대시보드 로딩 중...</div>
      <div class="sub-text">웹브라우저 내부에서 파이썬 가상환경(Pyodide)을 구동하고 있습니다. 최초 로딩 시 약 10~20초 정도 소요됩니다.</div>
    </div>
    <div id="root"></div>
    <script src="https://cdn.jsdelivr.net/npm/@stlite/mountable@0.59.0/build/stlite.js"></script>
    <script>
      // stlite 렌더링 감지 시 로딩 스피너 숨기기
      const observer = new MutationObserver((mutations, obs) => {{
        const streamlitRoot = document.querySelector('.stApp');
        if (streamlitRoot) {{
          const spinner = document.getElementById('spinner-container');
          if (spinner) {{
            spinner.style.display = 'none';
          }}
          obs.disconnect();
        }}
      }});
      observer.observe(document.body, {{
        childList: true,
        subtree: true
      }});

      stlite.mount({{
        requirements: ["pandas", "plotly", "requests", "python-dotenv", "koreanize-matplotlib", "matplotlib", "tabulate"],
        entrypoint: "app.py",
        files: {files_json}
      }}, document.getElementById("root"));
    </script>
  </body>
</html>
"""

    dist_dir = os.path.join(base_dir, "dist")
    os.makedirs(dist_dir, exist_ok=True)
    output_path = os.path.join(dist_dir, "korea_trip_dashboard.html")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"[Success] 정적 HTML 대시보드가 성공적으로 생성되었습니다: {output_path}")

if __name__ == "__main__":
    build()
