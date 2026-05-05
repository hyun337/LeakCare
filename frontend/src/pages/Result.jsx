import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getFullReport } from '../api/reportApi';
import '../styles/Result.css';

function Result() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadReport = async () => {
      try {
        setLoading(true);
        const res = await getFullReport(id);
        if (res.ok) {
          setReport(res.data);
        } else {
          setError('보고서를 불러오는데 실패했습니다.');
        }
      } catch (err) {
        console.error('보고서 로딩 실패:', err);
        setError('서버에 연결할 수 없습니다.');
      } finally {
        setLoading(false);
      }
    };
    loadReport();
  }, [id]);

  if (loading) return <div className="result-main"><p>불러오는 중...</p></div>;
  if (error) return <div className="result-main"><p style={{ color: 'red' }}>{error}</p></div>;
  if (!report) return <div className="result-main"><p>보고서가 없습니다.</p></div>;

  const isLeak = report.is_leaked;
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
              <tr><td>게시 URL</td><td>{report.target_url || report.url}</td></tr>
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
