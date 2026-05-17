import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getReports } from '../api/reportApi';
import '../styles/ReportList.css';

function ReportList() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState('전체');
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadReports = async () => {
      try {
        setLoading(true);
        setError('');
        const res = await getReports();
        const allData = res.ok && Array.isArray(res.data) ? res.data : [];
        // completed 상태인 것만 보고서로 표시
        setReports(allData.filter(r => r.status === 'completed'));
      } catch (err) {
        console.error('보고서 목록 로딩 실패:', err);
        setError('보고서 목록을 불러오는데 실패했습니다. 다시 시도해주세요.');
      } finally {
        setLoading(false);
      }
    };
    loadReports();
  }, []);

const isLeak = (report) => report.results?.length > 0;

  const filtered = filter === '전체'
    ? reports
    : reports.filter(r => filter === '유출 확인' ? isLeak(r) : !isLeak(r));

  if (loading) return <div className="report-list-main"><p>불러오는 중...</p></div>;
  if (error) return <div className="report-list-main"><p style={{ color: 'red' }}>{error}</p></div>;

  return (
    <div className="report-list-main">
      <div className="report-list-header">
        <div>
          <h2 className="report-list-title">결과 보고서</h2>
          <p className="report-list-sub">탐지 완료된 리스트를 확인하고 상세 보고서를 열람하세요.</p>
        </div>
      </div>

      <div className="report-filter-bar">
        {['전체', '유출 확인', '미확인'].map(f => (
          <button
            key={f}
            className={`report-filter-btn ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f}
          </button>
        ))}
      </div>

      <div className="report-table-wrap">
        <table className="report-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>탐지 URL</th>
              <th>판정 결과</th>
              <th>생성일</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', padding: '20px' }}>
                  보고서가 없습니다.
                </td>
              </tr>
            ) : (
              filtered.map((report) => (
                <tr key={report.task_id} onClick={() => navigate(`/reports/${report.task_id}`)}>
                  <td className="report-id">#{report.task_id?.slice(0, 8)}</td>
                  <td className="report-url">{report.url}</td>
                  <td>
                    <span className={`report-verdict ${isLeak(report) ? 'leak' : 'safe'}`}>
                      {isLeak(report) ? '유출 확인' : '미확인'}
                    </span>
                  </td>
                  <td className="report-date">
                    {new Date(report.created_at).toLocaleDateString('ko-KR')}
                  </td>
                  <td>
                    <button
                      className="report-detail-btn"
                      onClick={(e) => { e.stopPropagation(); navigate(`/reports/${report.task_id}`); }}
                    >
                      상세 보기
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ReportList;
