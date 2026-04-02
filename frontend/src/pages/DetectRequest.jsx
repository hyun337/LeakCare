import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Upload, AlertCircle, ImagePlus } from 'lucide-react';
import '../styles/DetectRequest.css';

// AppRouter에서 넘겨준 jobs와 setJobs를 props로 받기
const DetectRequest = ({ registeredPhotos, jobs, setJobs }) => {
  const navigate = useNavigate();
  const [url, setUrl] = useState('');
  const [selectedPhotoId, setSelectedPhotoId] = useState('');

  const selectedPhoto = registeredPhotos.find(p => p.id === Number(selectedPhotoId));

  // 폼 제출 
  const handleSubmit = (e) => {
    e.preventDefault();

    const newJob = {
      id: Date.now(), // 고유 ID 생성
      url: url,
      requestedAt: new Date().toLocaleString(), // 현재 시간 기록
      status: 'pending', // 초기 상태
      errorMessage: '',
    };

    // jobs 에 새 작업 추가 
    setJobs([newJob, ...jobs]);

    // 사용자 알림 및 페이지 이동 
    alert("탐지 요청이 정상적으로 제출되었습니다.");
    navigate('/jobs'); // 작업 목록 페이지
  };

  // 사진이 없을 때 예외 처리 
  if (registeredPhotos.length === 0) {
    return (
      <div className="detect-wrapper">
        <div className="no-photo-card" style={{ textAlign: 'center', padding: '60px' }}>
          <AlertCircle size={48} color="#6366f1" style={{ marginBottom: '20px' }} />
          <h2>등록된 사진이 없습니다!</h2>
          <p>탐지 요청을 위해 먼저 본인 사진을 등록해 주세요.</p>
          <button onClick={() => navigate('/photos')} className="btn-go-upload" style={{ marginTop: '20px' }}>
            <ImagePlus size={18} /> 사진 등록하러 가기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="detect-wrapper">
      <header className="page-header">
        <h1>새 탐지 요청</h1>
        <p>의심되는 URL과 내 사진을 대조하여 분석을 시작합니다. (일일 한도 5건)</p> 
      </header>

      {/* onSubmit에 handleSubmit 함수 연결 */}
      <form className="detect-form" onSubmit={handleSubmit}>
        <div className="section">
          <label><Search size={16} /> 의심 URL 입력</label> 
          <input 
            type="url" 
            placeholder="https://example.com" 
            value={url} 
            onChange={(e) => setUrl(e.target.value)} 
            required 
          />
        </div>

        <div className="section">
          <label><Upload size={16} /> 분석 대상 사진 선택 </label> 
          <select 
            className="face-select-dropdown" 
            value={selectedPhotoId} 
            onChange={(e) => setSelectedPhotoId(e.target.value)}
            required
          >
            <option value="">등록 사진을 선택하세요</option>
            {registeredPhotos.map(photo => (
              <option key={photo.id} value={photo.id}>
                {photo.name || `내 사진 (${photo.date})`}
              </option>
            ))}
          </select>
          
          {selectedPhoto && (
            <div className="selected-preview-min" style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '10px' }}>
              <img src={selectedPhoto.url} alt="Thumbnail" style={{ width: '50px', borderRadius: '8px' }} />
              <span style={{ fontSize: '13px', color: '#5C5CFF' }}>이 사진으로 분석을 진행합니다.</span>
            </div>
          )}
        </div>

        <button type="submit" className="btn-submit" disabled={!url || !selectedPhotoId}>
          탐지 요청 제출하기
        </button>
      </form>
    </div>
  );
};

export default DetectRequest;