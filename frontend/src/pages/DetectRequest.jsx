import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, ShieldCheck, AlertCircle, ImagePlus } from 'lucide-react';
import { submitDetectRequest } from '../api/detectApi';
import { getFaceStatus } from '../api/photoApi';
import BASE_URL from '../api/client';
import '../styles/DetectRequest.css';

const DetectRequest = () => {
  const navigate = useNavigate();
  const [url, setUrl] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [loading, setLoading] = useState(false);
  const [registeredPhotos, setRegisteredPhotos] = useState([]);
  const [photoCount, setPhotoCount] = useState(0);
  const [photosLoading, setPhotosLoading] = useState(true);

  useEffect(() => {
    const loadPhotos = async () => {
      try {
        const res = await getFaceStatus();
        if (res.ok) {
          setPhotoCount(res.data.photo_count || 0);
          if (res.data.photos) {
            const serverBase = BASE_URL.replace('/api/v1', '');
            const loaded = res.data.photos.map((p) => ({
              id: p.photo_index,
              photo_index: p.photo_index,
              url: p.url ? `${serverBase}${p.url}` : null,
            }));
            setRegisteredPhotos(loaded);
          }
        } else {
          setPhotoCount(-1); // API 실패 시 화면은 보여줌
        }
      } catch (err) {
        console.error('사진 목록 불러오기 실패:', err);
        setPhotoCount(-1); // 에러 시 화면은 보여줌
      } finally {
        setPhotosLoading(false);
      }
    };
    loadPhotos();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    try {
      setLoading(true);
      const res = await submitDetectRequest({ url });

      if (!res.ok) {
        if (Array.isArray(res.data?.detail)) {
          setErrorMsg(res.data.detail.map(err => err.msg).join('\n'));
        } else if (typeof res.data?.detail === 'string') {
          setErrorMsg(res.data.detail);
        } else {
          setErrorMsg('탐지 요청에 실패했습니다.');
        }
        return;
      }

      navigate('/jobs');
    } catch (error) {
      console.error('탐지 요청 오류:', error);
      setErrorMsg('서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.');
    } finally {
      setLoading(false);
    }
  };

  if (photosLoading) {
    return (
      <div className="detect-wrapper">
        <p style={{ textAlign: 'center', padding: '60px', color: '#999' }}>불러오는 중...</p>
      </div>
    );
  }

  if (photoCount === 0) {
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
        <p>의심되는 URL을 입력하면 등록된 모든 사진과 대조하여 분석을 시작합니다. (일일 한도 5건)</p>
      </header>

      <form className="detect-form" onSubmit={handleSubmit}>
        <div className="section">
          <label><Search size={16} /> 의심 URL 입력</label>
          <input
            type="url"
            placeholder="https://example.com"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value);
              setErrorMsg('');
            }}
            required
          />
        </div>

        <div className="section">
          <label><ShieldCheck size={16} /> 분석 대상 안내</label>
          <div className="selected-preview-min" style={{ display: 'flex', alignItems: 'center', gap: '15px', marginTop: '10px', padding: '15px', background: '#f8f9fa', borderRadius: '12px' }}>
            <div style={{ display: 'flex', gap: '5px' }}>
              {registeredPhotos.slice(0, 5).map(photo => (
                photo.url ? (
                  <img
                    key={photo.id}
                    src={photo.url}
                    alt="Thumbnail"
                    style={{ width: '40px', height: '40px', objectFit: 'cover', borderRadius: '6px', border: '1px solid #ddd' }}
                  />
                ) : (
                  <div
                    key={photo.id}
                    style={{ width: '40px', height: '40px', borderRadius: '6px', border: '1px solid #ddd', background: '#e0e0e0', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', color: '#999' }}
                  >
                    {photo.photo_index}
                  </div>
                )
              ))}
            </div>
            <div style={{ fontSize: '13px', color: '#5C5CFF', lineHeight: '1.4' }}>
              현재 등록된 <strong>{photoCount > 0 ? photoCount : '?'}장</strong>의 사진으로 <br/>
              실시간 교차 분석을 진행합니다.
            </div>
          </div>
        </div>

        {errorMsg && (
          <div style={{ background: '#fff0f0', border: '1px solid #ffcccc', borderRadius: '8px', padding: '12px', marginBottom: '10px' }}>
            <p style={{ color: 'red', fontSize: '0.85rem', margin: 0 }}>
              ⚠️ {errorMsg}
            </p>
          </div>
        )}

        <button type="submit" className="btn-submit" disabled={!url || loading}>
          {loading ? '요청 중...' : '탐지 요청 제출하기'}
        </button>
      </form>
    </div>
  );
};

export default DetectRequest;
