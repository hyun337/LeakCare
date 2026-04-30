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
import SettingsPage from "../pages/SettingsPage";
import DeleteRequest from "../pages/DeleteRequest";

function AppRouter() {
  const [photos, setPhotos] = useState([]);
  const [jobs, setJobs] = useState([]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route element={<MainLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          
          {/* 사진 관리*/}
          <Route 
            path="/photos" 
            element={<PhotoManagement photos={photos} setPhotos={setPhotos} />} 
          />
          
          {/* 탐지 요청*/}
          <Route 
            path="/detect" 
            element={<DetectRequest registeredPhotos={photos} jobs={jobs} setJobs={setJobs} />} 
          />
          
          {/* 작업 목록 */}
          <Route 
            path="/jobs" 
            element={<JobList jobs={jobs} setJobs={setJobs} />} 
          />
          <Route path="/reports/:reportId/delete-request" element={<DeleteRequest />} />
          <Route path="/reports" element={<ReportList />} />
          <Route path="/reports/:id" element={<Result />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRouter;
