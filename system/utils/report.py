import os
import time
import platform
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ─────────────────────────────
# [1] 한글 폰트 등록 (Tofu 현상 방지) 
# ─────────────────────────────
try:
    if platform.system() == "Darwin":  # Mac
        font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
    elif platform.system() == "Windows":  # Windows
        font_path = "C:/Windows/Fonts/malgun.ttf"
    else:  # Linux (Ubuntu 등)
        font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    
    # 폰트 파일이 존재하는지 확인 후 등록
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('KoreanFont', font_path))
    else:
        print(f"⚠️ 경고: 폰트 파일을 찾을 수 없습니다 ({font_path}). 영문으로 출력될 수 있습니다.")
except Exception as e:
    print(f"⚠️ 폰트 등록 중 오류 발생: {e}")

def generate_pdf_report(evidence_data, ai_results, output_path):
    """
    evidence_data: {ip, location, screenshot_path, target_url}
    ai_results: [{url, score, page_url}, ...]
    """
    # PDF 문서 생성을 위한 elements 준비
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    elements = []
    
    # 기본 스타일 시트 가져오기 및 한글 폰트 적용 
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = 'KoreanFont'

    # 1. 보고서 제목
    elements.append(Paragraph("<b>[LeakCare] 디지털 콘텐츠 유출 보고서</b>", styles['Title']))
    elements.append(Spacer(1, 12))

    # 2. 기본 정보 표 (Table)
    info_data = [
        ["항목", "내용"],
        ["대상 URL", evidence_data.get('target_url', 'N/A')],
        ["서버 IP", evidence_data.get('ip', 'N/A')],
        ["서버 위치", evidence_data.get('location', 'N/A')],
        ["채증 일시", time.strftime('%Y-%m-%d %H:%M:%S')]
    ]
    
    t = Table(info_data, colWidths=[100, 350])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'KoreanFont'), # 표 내부에도 폰트 적용
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    # 3. 채증 스크린샷 첨부
    elements.append(Paragraph("<b>[증거 1] 현장 채증 스크린샷</b>", styles['Heading2']))
    if os.path.exists(evidence_data.get('screenshot_path', '')):
        # 이미지 크기 최적화 (A4 너비에 맞춤)
        img = Image(evidence_data['screenshot_path'], width=450, height=250)
        elements.append(img)
    else:
        elements.append(Paragraph("<font color='red'>이미지 파일을 찾을 수 없습니다.</font>", styles['Normal']))
    elements.append(Spacer(1, 20))

    # 4. AI 분석 탐지 결과 표
    elements.append(Paragraph(f"<b>[증거 2] AI 유출 의심 탐지 결과 (총 {len(ai_results)}건)</b>", styles['Heading2']))
    
    analysis_data = [["순번", "유사도 점수", "이미지 원본 주소"]]
    for idx, res in enumerate(ai_results):
        # 긴 URL 생략 처리
        short_url = res['url'][:60] + "..." if len(res['url']) > 60 else res['url']
        analysis_data.append([idx + 1, f"{res['score']:.4f}", short_url])

    # 표가 비어있을 경우 예외 처리
    if len(ai_results) == 0:
        analysis_data.append(["-", "0.0000", "탐지된 의심 사례가 없습니다."])

    at = Table(analysis_data, colWidths=[40, 80, 330])
    at.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.orange), # 'brandy' 대신 표준색상 'orange' 사용
        ('FONTNAME', (0, 0), (-1, -1), 'KoreanFont'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(at)

    # 최종 PDF 빌드
    try:
        doc.build(elements)
        print(f"✅ PDF 보고서 생성 완료: {output_path}")
    except Exception as e:
        print(f"❌ PDF 빌드 중 오류 발생: {e}")
