import datetime
import os
import json
import hashlib

def get_project_root():
    """프로젝트 최상위 폴더(LeakCare/)의 절대 경로를 반환"""
    # 현재 파일(file_path.py) 위치에서 두 단계 위가 루트입니다.
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_evidence_path():
    """스크린샷 및 증거 저장을 위한 절대 경로를 생성"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_evidence.png"

    # 루트 폴더 기준 'evidence' 폴더 고정
    evidence_dir = os.path.join(get_project_root(), "evidence")
    
    if not os.path.exists(evidence_dir):
        os.makedirs(evidence_dir)

    output_path = os.path.join(evidence_dir, filename)
    return output_path, filename

def get_report_path(filename):
    """결과 파일명을 받아 리포트(PDF) 저장 절대 경로를 반환"""
    report_filename = filename.replace(".png", "_report.pdf")
    return os.path.join(get_project_root(), "evidence", report_filename)
