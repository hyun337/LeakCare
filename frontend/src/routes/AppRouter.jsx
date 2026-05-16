import React from "react";
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

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem('accessToken');
  return token ? children : <Navigate to="/login" replace />;
};

function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route element={<PrivateRoute><MainLayout /></PrivateRoute>}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/photos" element={<PhotoManagement />} />
          <Route path="/detect" element={<DetectRequest />} />
          <Route path="/jobs" element={<JobList />} />
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
