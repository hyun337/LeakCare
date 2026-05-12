import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import BASE_URL from '../api/client';
import '../styles/Result.css';

function Result() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const token = localStorage.getItem('accessToken');
        const res = await fetch(`${BASE_URL}/detection/full-report/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        setReport(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [id]);

  const handleDownloadPdf = () => {
    if (report?.report_path) {
      window.open(report.report_path, '_blank');
    } else {
      alert('PDF 파일이 아직 준비되지 않았습니다.');
    }
  };

  if (loading) return <div>불러오는 중...</div>;
  if (!report) return <div>보고서를 찾을 수 없습니다.</div>;

  const metadata = report.server_details?.metadata || report.analysis_result?.result?.metadata || {};
  const results = report.analysis_result?.result?.results || report.result?.results || [];
  const isLeak = results.length > 0;
  const topScore = results.length > 0
    ? Math.round(results[0].score * 100)
    : 0;

  const screenshotPath = report.analysis_result?.result?.screenshot_path || report.result?.screenshot_path;
  const serverBase = BASE_URL.replace('/api/v1', '');

  const formattedDate = metadata.collected_at
    ? new Date(metadata.collected_at).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })
    : '-';

  return (
    <div className="result-main">
      <button className="result-back-btn" onClick={() => navigate('/reports')}>
        ← 목록
      </button>
      <div className="result-header">
        <h2 className="result-title">보고서 상세</h2>
      </div>

      <div className="result-grid">
        <div className="result-card result-card-full">
          <div className="result-card-label">탐지 스크린샷</div>
          <div className="result-screenshot">
            {screenshotPath
              ? <img src={`${serverBase}${screenshotPath}`} alt="탐지 스크린샷" style={{ width: '100%' }} />
              : <span className="result-screenshot-placeholder">탐지 스크린샷 영역</span>
            }
          </div>
        </div>

        <div className="result-card">
          <div className="result-card-label">유사도 분석</div>
          <div className="result-score-row">
            <div className={`result-score-circle ${isLeak ? 'leak' : 'safe'}`}>
              <span className="result-score-num">{topScore}%</span>
              <span className="result-score-sub">유사도</span>
            </div>
            <p className="result-score-desc">
              {isLeak
                ? `등록된 얼굴과 ${topScore}% 일치합니다. 즉각적인 삭제 요청을 권장합니다.`
                : `유사도가 낮습니다. 유출 가능성이 낮습니다.`}
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
              <tr><td>게시 URL</td><td>{report.analysis_result?.url || report.url}</td></tr>
              <tr><td>수집 일시</td><td>{formattedDate}</td></tr>
              <tr><td>서버 IP</td><td>{metadata.ip_address || '-'}</td></tr>
              <tr><td>국가</td><td>{metadata.country} {metadata.city}</td></tr>
            </tbody>
          </table>
          <p className="result-ip-notice">IP·위치 정보는 ip-api.com 기반으로 정확도에 한계가 있을 수 있습니다.</p>
        </div>
      </div>

      <div className="result-actions">
        <button
          className="result-btn-pdf"
          onClick={handleDownloadPdf}
          disabled={!report.report_path && !report.analysis_result?.report_path}
        >
          PDF 다운로드
        </button>
        <button
          className="result-btn-delete"
          onClick={() => navigate(`/reports/${id}/delete-request`)}
        >
          삭제 요청서 확인
        </button>
      </div>
    </div>
  );
}

export default Result;
