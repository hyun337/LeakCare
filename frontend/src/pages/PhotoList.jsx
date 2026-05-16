import React, { useState, useEffect } from "react";
import { Trash2, ImageIcon, UserCircle } from 'lucide-react';
import { COMMON_HEADERS } from '../api/client';

function PhotoCard({ photo, onDelete }) {
  const [imgUrl, setImgUrl] = useState(null);

  useEffect(() => {
    if (!photo.url) return;
    fetch(photo.url, { headers: COMMON_HEADERS })
      .then(res => res.blob())
      .then(blob => setImgUrl(URL.createObjectURL(blob)));
  }, [photo.url]);

  return (
    <div className="photo-card-item">
      <div className="photo-card-image">
        {imgUrl
          ? <img src={imgUrl} alt="User Face" />
          : <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f0f0f0', borderRadius: '8px' }}>
              <UserCircle size={48} color="#aaa" />
            </div>
        }
      </div>
      <div className="photo-card-footer">
        <span className="photo-upload-date">{photo.date}</span>
        <button
          className="photo-delete-action"
          onClick={() => onDelete(photo)}
          title="삭제"
        >
          <Trash2 size={16} />
          <span>삭제</span>
        </button>
      </div>
    </div>
  );
}

function PhotoList({ photos, onDelete }) {
  if (photos.length === 0) {
    return (
      <div className="empty-photo-state">
        <ImageIcon size={48} />
        <p>등록된 사진이 없습니다. 사진을 추가해 주세요.</p>
      </div>
    );
  }

  return (
    <div className="photo-modern-grid">
      {photos.map((photo) => (
        <PhotoCard key={photo.id} photo={photo} onDelete={onDelete} />
      ))}
    </div>
  );
}

export default PhotoList;
