import React, { useState, useEffect } from 'react'; 
import { Link } from 'react-router-dom';
import '../styles/dashboard.css';

function Dashboard() {
  //  실시간 시간을 저장할 상태
  const [updateTime, setUpdateTime] = useState('');

  // 페이지가 로드될 때 현재 시간을 포맷에 맞춰 설정
  useEffect(() => {
    const now = new Date();
    const formattedDate = `${now.getFullYear()}. ${String(now.getMonth() + 1).padStart(2, '0')}. ${String(now.getDate()).padStart(2, '0')}.`;
    
    const hours = now.getHours();
    const ampm = hours >= 12 ? '오후' : '오전';
    const displayHours = hours % 12 || 12; 
    const minutes = String(now.getMinutes()).padStart(2, '0');
    
    const finalString = `${formattedDate} ${ampm} ${displayHours}:${minutes}`;
    setUpdateTime(finalString);
  }, []);

  // 샘플 데이터
  const recentLogs = [
    { id: 1, name: '영상_분석_01.mp4', date: '2026-03-17 14:20', score: 98 },
    { id: 2, name: '이미지_샘플_22.jpg', date: '2026-03-16 09:11', score: 2 },
    { id: 3, name: 'SNS_프로필_검사.png', date: '2026-03-16 18:45', score: 85 },
    { id: 4, name: '파일_검토_요청.zip', date: '2026-03-16 10:00', score: 50 },
    { id: 5, name: '테스트_파일_05.mp4', date: '2026-03-15 21:30', score: 5 },
  ];

  const getStatusInfo = (score) => {
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
            <div className="stat-value">128</div>
          </div>
        </div>
        <div className="large-stat-card">
          <div className="stat-icon delete-icon">🗑️</div>
          <div className="stat-info">
            <div className="stat-label">삭제 요청</div>
            <div className="stat-value">42</div>
          </div>
        </div>
        <div className="large-stat-card">
          <div className="stat-icon progress-icon">⌛</div>
          <div className="stat-info">
            <div className="stat-label">진행 중</div>
            <div className="stat-value">15</div>
          </div>
        </div>
      </section>

      <section className="activity-section">
        <div className="section-header">
          <h3>최근 탐지 로그</h3>
          <Link to="/reports" className="view-all">전체보기 &gt;</Link>
        </div>
        
        <div className="table-container">
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
                const status = getStatusInfo(log.score);
                return (
                  <tr key={log.id}>
                    <td className="file-name">{log.name}</td>
                    <td className="analysis-date">{log.date}</td>
                    <td>
                      <div 
                        className={`progress-circle ${status.class}`} 
                        style={{ '--percent': log.score }}
                      >
                        <span className="percent-text">{log.score}%</span>
                      </div>
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
        </div>
      </section>
    </div>
  );
}

export default Dashboard;