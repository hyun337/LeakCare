import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getFullReport } from '../api/reportApi';
import BASE_URL, { COMMON_HEADERS } from '../api/client';
import '../styles/Result.css';

const SYSTEM_SERVER_URL = 'https://aloof-absurd-altitude.ngrok-free.dev';



function ScreenshotImg({ src }) {
  const [imgUrl, setImgUrl] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!src) return;
    fetch(src, { headers: COMMON_HEADERS })
      .then((res) => {
        if (!res.ok) { setError(true); return; }
        return res.blob();
      })
      .then((blob) => { if (blob) setImgUrl(URL.createObjectURL(blob)); })
      .catch(() => setError(true));
  }, [src]);

  if (error || !src) return <span className="result-screenshot-placeholder">탐지 스크린샷 영역</span>;
  return imgUrl
    ? <img src={imgUrl} alt="탐지 스크린샷" style={{ width: '100%' }} />
    : <span className="result-screenshot-placeholder">탐지 스크린샷 영역</span>;
}

function Result() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const res = await getFullReport(id);
        console.log('full-report 응답:', JSON.stringify(res.data, null, 2));
        if (res.ok) {
          setReport(res.data);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [id]);

  const handleDownloadPdf = () => {
    const path = report?.analysis_result?.report_path || report?.report_path;
    if (path) {
      window.open(path, '_blank');
    } else {
      alert('PDF 파일이 아직 준비되지 않았습니다.');
    }
  };

  if (loading) return <div>불러오는 중...</div>;
  if (!report) return <div>보고서를 찾을 수 없습니다.</div>;

  // results 추출 - BE가 task 최상위에 저장하므로 두 경로 모두 시도
  const analysisResult = report?.analysis_result ?? {};
  const results = analysisResult?.results ?? [];

  const hasMatchedResult = results.some((r) => r.matched === true);
  const hasAnyResult = results.length > 0;
  const removalText = analysisResult?.removal_request_text ?? '';
  const isSafeByText = removalText.includes('안전합니다') || removalText.includes('발견되지 않았습니다');

  // 최종 판정: matched 결과가 있거나, results가 있고 안전 텍스트가 없으면 유출
  const isLeak = hasMatchedResult || (hasAnyResult && !isSafeByText);

  // topScore: score는 0~1 사이 float이므로 *100
  const topScore =
    results.length > 0
      ? Math.round(Math.max(...results.map((r) => r.score ?? 0)) * 100)
      : 0;

  // 딥페이크 여부
  const hasDeepfake = results.some((r) => r.is_deepfake === true);

  const metadata = report.server_details || analysisResult?.metadata || {};
  const screenshotPath = analysisResult?.screenshot_path;
  const formattedDate = metadata.collected_at
    ? new Date(metadata.collected_at).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })
    : '-';

  console.log('=== 판정 디버그 ===');
  console.log('results:', results);
  console.log('hasMatchedResult:', hasMatchedResult);
  console.log('hasAnyResult:', hasAnyResult);
  console.log('removalText:', removalText?.slice(0, 50));
  console.log('isLeak 최종:', isLeak);
  console.log('topScore:', topScore);

  console.log('screenshotPath:', screenshotPath);
  console.log('최종 URL:', screenshotPath ? `${SYSTEM_SERVER_URL}${screenshotPath}` : null);

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
            <ScreenshotImg
              src={screenshotPath ? `${SYSTEM_SERVER_URL}${screenshotPath}` : null}
            />
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
              <tr>
                <td>판정 결과</td>
                <td>
                  <span className={`result-verdict ${isLeak ? 'leak' : 'safe'}`}>
                    {isLeak ? '유출 확인' : '미확인'}
                  </span>
                </td>
              </tr>
              {hasDeepfake && (
                <tr>
                  <td>딥페이크</td>
                  <td>
                    <span className="result-verdict leak">딥페이크 감지</span>
                  </td>
                </tr>
              )}
              <tr>
                <td>탐지 건수</td>
                <td>{results.length}건</td>
              </tr>
              <tr>
                <td>게시 URL</td>
                <td>{analysisResult?.url || report.url}</td>
              </tr>
              <tr>
                <td>수집 일시</td>
                <td>{formattedDate}</td>
              </tr>
              <tr>
                <td>서버 IP</td>
                <td>{metadata.ip_address || '-'}</td>
              </tr>
              <tr>
                <td>국가</td>
                <td>
                  {metadata.country || '-'} {metadata.city || ''}
                </td>
              </tr>
            </tbody>
          </table>
          <p className="result-ip-notice">
            IP·위치 정보는 ip-api.com 기반으로 정확도에 한계가 있을 수 있습니다.
          </p>
        </div>
      </div>

      <div className="result-actions">
        <button
          className="result-btn-pdf"
          onClick={handleDownloadPdf}
          disabled={!analysisResult?.report_path && !report?.report_path}
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
