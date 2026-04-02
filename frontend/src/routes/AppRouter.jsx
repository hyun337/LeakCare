import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "../pages/Login";
import Register from "../pages/Register";
import Dashboard from "../pages/Dashboard";
import PhotoManagement from "../pages/PhotoManagement";
import DetectRequest from "../pages/DetectRequest";
import MainLayout from "../components/layout/MainLayout";
import JobList from "../pages/JobList";
import ReportList from "../pages/ReportList";
import Result from "../pages/Result";

function AppRouter() {
  // 공유 상태: 등록된 사진 목록
  const [photos, setPhotos] = useState([
    { id: 1, url: "https://via.placeholder.com/150", date: "2026-03-20", name: "샘플 정면 사진", status: "Safe" },
  ]);

  // 공유 상태: 실시간 탐지 작업 목록
  // 초기 데이터 넣어두어 테스트 진행 
  const [jobs, setJobs] = useState([
    {
      id: 101,
      url: 'https://example.com/leak-post-01',
      requestedAt: '2026-03-31 14:20',
      status: 'completed',
      errorMessage: '',
    }
  ]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route element={<MainLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          
          {/* 사진 관리: 사진 목록과 수정 함수 전달 */}
          <Route 
            path="/photos" 
            element={<PhotoManagement photos={photos} setPhotos={setPhotos} />} 
          />
          
          {/* 탐지 요청: [핵심] 사진 목록(선택용)과 작업 목록 수정 함수(추가용) 전달 */}
          <Route 
            path="/detect" 
            element={<DetectRequest registeredPhotos={photos} jobs={jobs} setJobs={setJobs} />} 
          />
          
          {/* 작업 목록: [핵심] 실시간 상태 업데이트를 위해 jobs와 setJobs 전달 */}
          <Route 
            path="/jobs" 
            element={<JobList jobs={jobs} setJobs={setJobs} />} 
          />

          <Route path="/reports" element={<ReportList />} />
          <Route path="/reports/:id" element={<Result />} />
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRouter;