import React, { useState } from "react";
import { Upload, X, User, AlertCircle } from "lucide-react";
import PhotoList from "./PhotoList";
import "../styles/photo.css";

function PhotoManagement({ photos, setPhotos }) {
  const MAX_PHOTOS = 5;
  const [pendingFile, setPendingFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [faceDetectionError, setFaceDetectionError] = useState(null);

  const isPhotoLimitReached = photos.length >= MAX_PHOTOS;

  const handleFileSelect = (files) => {
    if (isPhotoLimitReached) {
      alert("최대 5장까지 등록 가능합니다. 기존 사진을 삭제해 주세요.");
      return;
    }
    const file = files[0];
    if (!file) return;

    const allowedTypes = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
    if (!allowedTypes.includes(file.type)) {
      alert("JPG, PNG, WEBP 형식만 업로드 가능합니다.");
      return;
    }

    setFaceDetectionError(null);
    setPendingFile({
      id: Date.now(),
      previewUrl: URL.createObjectURL(file),
    });
  };

  const handleStartScan = () => {
    setIsAnalyzing(true);
    setFaceDetectionError(null);

    // 2.5초후 반환하도록 테스트 진행 (80% 확률로 성공 가정)
    setTimeout(() => {
      const isFaceDetected = Math.random() > 0.2; 

      if (isFaceDetected) {
        const newPhoto = {
          id: Date.now(),
          url: pendingFile.previewUrl,
          date: new Date().toISOString().split("T")[0],
          name: `등록 사진 ${photos.length + 1}`,
          status: "Safe",
        };
        setPhotos([...photos, newPhoto]);
        setPendingFile(null);
        alert("얼굴 분석이 완료되었습니다.");
      } else {
        // 실패 시: CSS에 정의된 메시지 출력을 위한 상태 업데이트
        setFaceDetectionError("얼굴을 찾을 수 없습니다. 다시 시도해 주세요.");
      }
      setIsAnalyzing(false);
    }, 2500);
  };

  return (
    <div className="photos-wrapper">
      {/* AI 분석 중 로딩  */}
      {isAnalyzing && (
        <div className="analysis-overlay">
          <div className="analysis-card">
            <div className="scanner-container">
              <div className="scanner-line"></div>
              <User size={48} color="#5C5CFF" />
            </div>
            <h3 className="analysis-title">AI 얼굴 분석 중...</h3>
            <p className="analysis-subtext">본인 확인을 정밀하게 진행 중입니다.</p>
          </div>
        </div>
      )}

      <header className="page-header">
        <div className="header-title-row">
          <h1>내 사진 관리</h1>
          <span className="photo-count-badge">{photos.length} / {MAX_PHOTOS}장</span>
        </div>
        <p className="page-desc">사진을 업로드하여 분석을 진행하세요. 최대 5장까지 등록 가능합니다.</p>
      </header>

      <section className="upload-container">
        {!pendingFile && !isPhotoLimitReached ? (
          <div
            className={`modern-dropzone ${isDragging ? "active" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={(e) => { e.preventDefault(); setIsDragging(false); handleFileSelect(Array.from(e.dataTransfer.files)); }}
            onClick={() => document.getElementById("fileInput").click()}
          >
            <input id="fileInput" type="file" hidden accept="image/*" onChange={(e) => handleFileSelect(Array.from(e.target.files))} />
            <div className="dropzone-inner">
              <div className="dropzone-icon-bg"><Upload size={32} /></div>
              <p className="main-drop-text">클릭하거나 사진을 드래그하여 추가</p>
              <p className="sub-drop-text">JPG, PNG, WEBP (최대 10MB)</p>
            </div>
          </div>
        ) : pendingFile && (
          <div className="pending-file-preview">
            {/* 에러 발생 시 빨간 테두리 적용 */}
            <div className={`preview-card ${faceDetectionError ? "has-error" : ""}`}>
              <img src={pendingFile.previewUrl} alt="Preview" />
              <button className="preview-close-btn" onClick={() => setPendingFile(null)}>
                <X size={18} />
              </button>
              
              {/* 오류 시 메시지 출력 */}
              {faceDetectionError && (
                <div className="error-badge">
                  <AlertCircle size={14} style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }} />
                  {faceDetectionError}
                </div>
              )}
            </div>

            <div className="preview-action">
              <button className="scan-trigger-btn" onClick={handleStartScan}>
                {faceDetectionError ? "다시 시도" : "얼굴 등록"}
              </button>
            </div>
          </div>
        )}

        {isPhotoLimitReached && !pendingFile && (
          <div className="photo-limit-box">
            <h3 className="photo-limit-title">등록 한도 도달</h3>
            <p className="photo-limit-text">최대 5장까지만 등록 가능합니다. 기존 사진을 삭제하고 진행해주세요.</p>
          </div>
        )}
      </section>

      <section className="registered-list-section">
        <h3 className="section-title">등록된 내 사진</h3>
        <div className="list-content-box">
          <PhotoList photos={photos} onDelete={(id) => setPhotos(photos.filter(p => p.id !== id))} />
        </div>
      </section>
    </div>
  );
}

export default PhotoManagement;