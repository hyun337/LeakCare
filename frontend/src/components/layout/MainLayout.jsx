import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import '../../styles/layout.css';

function LeakCareLogo() {                               // LeakCare로고
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
      <svg width="28" height="28" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <circle cx="18" cy="18" r="18" fill="#534AB7" />
        <circle cx="18" cy="18" r="9" stroke="#EEEDFE" strokeWidth="2" />
        <circle cx="18" cy="18" r="3" fill="#EEEDFE" />
      </svg>
      <span style={{ fontSize: '20px', fontWeight: 800, letterSpacing: '-0.5px', lineHeight: 1, color: '#4f46e5', fontFamily: "'Pretendard', -apple-system, sans-serif" }}>
        LeakCare
      </span>
    </div>
  );
}

function MainLayout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    window.location.href = '/login';
  };

  return (
    <div className="dashboard-wrapper">
      <nav className="top-navigation">
        <div className="nav-container">
          <div className="nav-left">
            <NavLink to="/dashboard" className="logo-link">
              <LeakCareLogo />
            </NavLink>
          </div>

          <div className="nav-center">
            <NavLink to="/dashboard" end className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              메인 현황
            </NavLink>
            <NavLink to="/photos" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              내 사진 관리
            </NavLink>
            <NavLink to="/detect" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              탐지 요청
            </NavLink>
            <NavLink to="/jobs" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              작업 목록
            </NavLink>
            <NavLink to="/reports" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              결과 보고서
            </NavLink>
          </div>

          <div className="nav-right">
            <button className="nav-icon-btn">?</button>
            <button className="nav-icon-btn" onClick={() => navigate('/settings')}>👤</button>
            <button onClick={handleLogout} className="logout-btn-minimal">
              로그아웃
            </button>
          </div>
        </div>
      </nav>
      <main className="dashboard-content">
        <Outlet />
      </main>
    </div>
  );
}

export default MainLayout;
