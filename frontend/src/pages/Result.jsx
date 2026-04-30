import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import '../styles/Result.css';

function Result() {
  const { id } = useParams();
  const navigate = useNavigate();

  // 더미데이터 임시용
  const report = {
    task_id: id,
    is_leaked: true,
    score: 94.5,
    ip_address: '123.456.78.9',
    country: 'South Korea',
    city: 'Seoul',
    target_url: 'https://example.com/site1',
    collected_at: '2026-03-25T14:32:00Z',
    screenshot_path: null,
  };

  const isLeak = report.is_leaked;

  // 날짜 포맷 변환 
  const formattedDate = report.collected_at
    ? new Date(report.collected_at).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })
    : '-';

  return (
    <div className="result-main">
      <button className="result-back-btn" onClick={() => navigate('/reports')}>
        ← 목록
      </button>

      <div className="result-header">
        <h2 className="result-title">보고서 상세</h2>
        <span className="result-id"></span>
      </div>

      <div className="result-grid">
        <div className="result-card result-card-full">
          <div className="result-card-label">탐지 스크린샷</div>
          <div className="result-screenshot">
            {report.screenshot_path
              ? <img src={report.screenshot_path} alt="탐지 스크린샷" style={{ width: '100%' }} />
              : <span className="result-screenshot-placeholder">탐지 스크린샷 영역</span>
            }
          </div>
        </div>

        <div className="result-card">
          <div className="result-card-label">유사도 분석</div>
          <div className="result-score-row">
            <div className={`result-score-circle ${isLeak ? 'leak' : 'safe'}`}>
              <span className="result-score-num">{report.score}%</span>
              <span className="result-score-sub">유사도</span>
            </div>
            <p className="result-score-desc">
              {isLeak
                ? `등록된 얼굴과 ${report.score}% 일치합니다. 즉각적인 삭제 요청을 권장합니다.`
                : `유사도가 낮습니다(${report.score}%). 유출 가능성이 낮습니다.`}
            </p>
          </div>
        </div>

        <div className="result-card">
          <div className="result-card-label">증거데이터</div>
          <table className="result-meta-table">
            <tbody>
              <tr><td>판정 결과</td><td>
                <span className={`result-verdict ${isLeak ? 'leak' : 'safe'}`}>
                  {isLeak ? '유출 확인' : '미확인'}
                </span>
              </td></tr>
              <tr><td>게시 URL</td><td>{report.target_url}</td></tr>
              <tr><td>수집 일시</td><td>{formattedDate}</td></tr>
              <tr><td>서버 IP</td><td>{report.ip_address}</td></tr>
              <tr><td>국가</td><td>{report.country} {report.city}</td></tr>
            </tbody>
          </table>
          <p className="result-ip-notice">IP·위치 정보는 ip-api.com 기반으로 정확도에 한계가 있을 수 있습니다.</p>
        </div>
      </div>

      <div className="result-actions">
        <button className="result-btn-pdf">PDF 다운로드</button>
        <button className="result-btn-delete" onClick={() => navigate(`/reports/${id}/delete-request`)}>
          삭제 요청서 확인
        </button>
      </div>
    </div>
  );
}

export default Result;
