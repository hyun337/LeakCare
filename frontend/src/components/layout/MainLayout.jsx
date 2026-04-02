import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import '../../styles/layout.css';

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
              <span className="logo">📸 LeakCare</span>
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
            <NavLink to="/reports" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              결과 보고서
            </NavLink>
          </div>

          <div className="nav-right">
            <button className="nav-icon-btn">?</button>
            <button className="nav-icon-btn">👤</button>
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