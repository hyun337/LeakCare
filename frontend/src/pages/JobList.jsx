import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Clock3,
  LoaderCircle,
  CheckCircle2,
  XCircle,
  RotateCcw,
  RefreshCw,
  Search,
  FileText,
  AlertCircle
} from 'lucide-react';
import '../styles/JobList.css';

const JobList = ({ jobs, setJobs }) => {
  const navigate = useNavigate();
  const [keyword, setKeyword] = useState('');
  const [lastUpdated, setLastUpdated] = useState(new Date());

  // 5초 간격 자동 테스트 해보기 
  useEffect(() => {
    const interval = setInterval(() => {
      setJobs((prevJobs) =>
        prevJobs.map((job) => {
          if (job.status === 'pending') return { ...job, status: 'processing' };
          if (job.status === 'processing') return { ...job, status: 'completed' };
          return job;
        })
      );
      setLastUpdated(new Date());
    }, 5000);

    return () => clearInterval(interval);
  }, [setJobs]);

  const handleRetry = (jobId) => {
    setJobs((prevJobs) =>
      prevJobs.map((job) =>
        job.id === jobId ? { ...job, status: 'pending', errorMessage: '', requestedAt: new Date().toLocaleString() } : job
      )
    );
  };

  const getStatusLabel = (status) => {
    const labels = { pending: '대기', processing: '분석중', completed: '완료', failed: '오류' };
    return labels[status] || '알 수 없음';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return <Clock3 size={14} />;
      case 'processing': return <LoaderCircle size={14} className="spin-icon" />;
      case 'completed': return <CheckCircle2 size={14} />;
      case 'failed': return <XCircle size={14} />;
      default: return null;
    }
  };

  const filteredJobs = jobs.filter((job) => {
    const target = `${job.id} ${job.url} ${getStatusLabel(job.status)}`.toLowerCase();
    return target.includes(keyword.toLowerCase());
  });

  return (
    <div className="joblist-wrapper">
      <header className="joblist-header">
        <div className="header-text">
          <h1>작업 목록</h1>
          <p>탐지 엔진이 실시간으로 URL을 분석 중입니다.</p>
        </div>
        <button type="button" className="refresh-btn" onClick={() => setLastUpdated(new Date())}>
          <RefreshCw size={16} /> 새로고침
        </button>
      </header>

      {/* 요약 카드 섹션 */}
      <section className="joblist-summary">
        {['전체', '대기', '분석중', '완료', '오류'].map((label, idx) => {
          const statusMap = [null, 'pending', 'processing', 'completed', 'failed'];
          const count = statusMap[idx] ? jobs.filter(j => j.status === statusMap[idx]).length : jobs.length;
          const statusClass = statusMap[idx] || 'all';
          return (
            <div key={label} className={`summary-card ${statusClass}`}>
              <span className="summary-label">{label}</span>
              <strong className="summary-count">{count}</strong>
            </div>
          );
        })}
      </section>

      <section className="joblist-topbar">
        <div className="search-box">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="작업 ID, URL, 상태로 검색..."
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
          />
        </div>
        <div className="polling-info">
          <div className="dot-blink"></div>
          <span className="polling-text">5초 간격 자동 갱신 중</span>
          <span className="time-label">{lastUpdated.toLocaleTimeString()}</span>
        </div>
      </section>

      <div className="joblist-table-container">
        {/* 테이블 헤더 */}
        <div className="joblist-table-head">
          <div className="col-id">작업 ID</div>
          <div className="col-url">의심 URL</div>
          <div className="col-date">요청 일시</div>
          <div className="col-status">상태</div>
          <div className="col-action">관리</div>
        </div>

        {/* 테이블 본문 */}
        <div className="joblist-table-body">
          {filteredJobs.length === 0 ? (
            <div className="empty-state">
              <AlertCircle size={32} />
              <p>해당하는 작업 내역이 없습니다.</p>
            </div>
          ) : (
            filteredJobs.map((job) => (
              <div key={job.id} className="joblist-row">
                <div className="col-id">#{job.id}</div>
                <div className="col-url" title={job.url}>{job.url}</div>
                <div className="col-date">{job.requestedAt}</div>
                <div className="col-status">
                  <span className={`status-badge ${job.status}`}>
                    {getStatusIcon(job.status)} {getStatusLabel(job.status)}
                  </span>
                </div>
                <div className="col-action">
                  {job.status === 'completed' ? (
                    <button className="btn-report" onClick={() => navigate(`/reports/${job.id}`)}>
                      <FileText size={14} /> 보고서
                    </button>
                  ) : job.status === 'failed' ? (
                    <button className="btn-retry" onClick={() => handleRetry(job.id)}>
                      <RotateCcw size={14} /> 재시도
                    </button>
                  ) : (
                    <span className="analyzing-text">분석 중...</span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default JobList;