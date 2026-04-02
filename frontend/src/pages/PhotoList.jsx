import React from "react";
import { Trash2, ImageIcon } from 'lucide-react';

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
        <div key={photo.id} className="photo-card-item">
          <div className="photo-card-image">
            <img src={photo.url} alt="User Face" />
          </div>
          <div className="photo-card-footer">
            <span className="photo-upload-date">{photo.date}</span>
            <button
              className="photo-delete-action"
              onClick={() => onDelete(photo.id)}
              title="삭제"
            >
              <Trash2 size={16} />
              <span>삭제</span>
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

export default PhotoList;