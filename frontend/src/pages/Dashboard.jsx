import React, { useState, useEffect } from 'react'; 
import { Link } from 'react-router-dom';
import { getDetectionHistory } from '../api/jobApi';
import '../styles/dashboard.css';

function Dashboard() {
  const [updateTime, setUpdateTime] = useState('');
  const [stats, setStats] = useState({ total: 0, deleteRequest: 0, inProgress: 0 });
  const [recentLogs, setRecentLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const now = new Date();
    const formattedDate = `${now.getFullYear()}. ${String(now.getMonth() + 1).padStart(2, '0')}. ${String(now.getDate()).padStart(2, '0')}.`;
    const hours = now.getHours();
    const ampm = hours >= 12 ? '오후' : '오전';
    const displayHours = hours % 12 || 12; 
    const minutes = String(now.getMinutes()).padStart(2, '0');
    setUpdateTime(`${formattedDate} ${ampm} ${displayHours}:${minutes}`);
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const historyRes = await getDetectionHistory();
        const history = historyRes.ok && Array.isArray(historyRes.data) ? historyRes.data : [];

        const total = history.length;
        const inProgress = history.filter(h =>
          h.status === 'pending' || h.status === 'processing'
        ).length;
        const deleteRequest = history.filter(h => h.status === 'completed').length;

        setStats({ total, deleteRequest, inProgress });

        const recent = [...history]
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
          .slice(0, 5)
          .map(h => ({
            id: h.task_id,
            name: h.target_name || h.url,
            date: new Date(h.created_at).toLocaleString('ko-KR'),
            score: h.result?.percent ?? null,
            status: h.status,
          }));

        setRecentLogs(recent);
      } catch (err) {
        console.error('대시보드 데이터 로딩 실패:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getStatusInfo = (score, status) => {
    if (status === 'pending') return { text: '대기', class: 'warning' };
    if (status === 'processing') return { text: '분석중', class: 'warning' };
    if (status === 'error') return { text: '오류', class: 'danger' };
    if (score === null || score === undefined) return { text: '-', class: 'safe' };
    if (score >= 85) return { text: '위험', class: 'danger' };
    if (score >= 40) return { text: '의심', class: 'warning' };
    return { text: '안전', class: 'safe' };
  };

  return (
    <div className="dashboard-main">
      <header className="content-header">
        <div className="header-title">
          <h2>메인 현황</h2>
          <p>최근 업데이트: {updateTime}</p> 
        </div>
        <Link to="/detect" className="btn-request-direct">새 탐지 요청</Link>
      </header>

      <section className="stats-container">
        <div className="large-stat-card">
          <div className="stat-icon dashboard-search-icon">🔍</div>
          <div className="stat-info">
            <div className="stat-label">전체 탐지</div>
            <div className="stat-value">{loading ? '-' : stats.total}</div>
          </div>
        </div>
        <div className="large-stat-card">
          <div className="stat-icon delete-icon">🗑️</div>
          <div className="stat-info">
            <div className="stat-label">삭제 요청</div>
            <div className="stat-value">{loading ? '-' : stats.deleteRequest}</div>
          </div>
        </div>
        <div className="large-stat-card">
          <div className="stat-icon progress-icon">⌛</div>
          <div className="stat-info">
            <div className="stat-label">진행 중</div>
            <div className="stat-value">{loading ? '-' : stats.inProgress}</div>
          </div>
        </div>
      </section>

      <section className="activity-section">
        <div className="section-header">
          <h3>최근 탐지 로그</h3>
          <Link to="/reports" className="view-all">전체보기 &gt;</Link>
        </div>
        
        <div className="table-container">
          {loading ? (
            <p style={{ textAlign: 'center', padding: '20px', color: '#999' }}>불러오는 중...</p>
          ) : recentLogs.length === 0 ? (
            <p style={{ textAlign: 'center', padding: '20px', color: '#999' }}>탐지 기록이 없습니다.</p>
          ) : (
            <table className="activity-table">
              <thead>
                <tr>
                  <th>파일명</th>
                  <th>분석 일시</th>
                  <th>탐지 확률</th>
                  <th>상태</th>
                </tr>
              </thead>
              <tbody>
                {recentLogs.map((log) => {
                  const status = getStatusInfo(log.score, log.status);
                  return (
                    <tr key={log.id}>
                      <td className="file-name">{log.name}</td>
                      <td className="analysis-date">{log.date}</td>
                      <td>
                        {log.score !== null && log.score !== undefined ? (
                          <div 
                            className={`progress-circle ${status.class}`} 
                            ref={el => el && el.style.setProperty('--percent', log.score)}
                          >
                            <span className="percent-text">{log.score}%</span>
                          </div>
                        ) : (
                          <span style={{ color: '#999' }}>-</span>
                        )}
                      </td>
                      <td>
                        <span className={`status-label ${status.class}`}>
                          {status.text}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </div>
  );
}

export default Dashboard;
