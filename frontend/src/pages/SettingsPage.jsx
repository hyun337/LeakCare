import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/SettingsPage.css';
import { deleteUser } from '../api/userApi'; // ✅ 추가

function SettingsPage() {
  const navigate = useNavigate();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [emailAlert, setEmailAlert] = useState(true);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [pwMessage, setPwMessage] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false); // ✅ 추가

  const handlePasswordChange = (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setPwMessage({ type: 'error', text: '새 비밀번호가 일치하지 않습니다.' });
      return;
    }
    if (newPassword.length < 6) {
      setPwMessage({ type: 'error', text: '비밀번호는 6자 이상이어야 합니다.' });
      return;
    }
    setPwMessage({ type: 'success', text: '비밀번호가 변경되었습니다.' });
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
  };

  // 실제 API 연결 테스트 완료 
  const handleDeleteAccount = async () => {
    const userId = localStorage.getItem('userId');
    setDeleteLoading(true);

    const result = await deleteUser({ userId });
    setDeleteLoading(false);

    if (result.ok) {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('userId');
      localStorage.removeItem('userEmail');
      localStorage.removeItem('userName');
      navigate('/login');
    } else {
      setShowDeleteModal(false);
      alert('탈퇴 처리 중 오류가 발생했습니다. 다시 시도해주세요.');
    }
  };

  return (
    <div className="settings-main">
      <div className="settings-header">
        <h2 className="settings-title">계정 설정</h2>
        <p className="settings-sub">내 계정 정보 및 알림 관리.</p>
      </div>

      {/* 비밀번호 변경 */}
      <div className="settings-card">
        <div className="settings-card-label">비밀번호 변경</div>
        <form onSubmit={handlePasswordChange} className="settings-form">
          <div className="settings-field">
            <label>현재 비밀번호</label>
            <input
              type="password"
              placeholder="현재 비밀번호 입력"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
            />
          </div>
          <div className="settings-field">
            <label>새 비밀번호</label>
            <input
              type="password"
              placeholder="새 비밀번호 입력"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
          </div>
          <div className="settings-field">
            <label>새 비밀번호 확인</label>
            <input
              type="password"
              placeholder="새 비밀번호 재입력"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>
          {pwMessage && (
            <p className={`settings-msg ${pwMessage.type}`}>{pwMessage.text}</p>
          )}
          <button type="submit" className="settings-btn-primary">변경하기</button>
        </form>
      </div>

      {/* 알림 설정 */}
      <div className="settings-card">
        <div className="settings-card-label">알림 설정</div>
        <div className="settings-toggle-row">
          <div>
            <div className="settings-toggle-title">이메일 알림</div>
            <div className="settings-toggle-desc">탐지 완료 시 이메일로 알림을 받습니다.</div>
          </div>
          <div
            className={`toggle-track ${emailAlert ? 'on' : ''}`}
            onClick={() => setEmailAlert(!emailAlert)}
          >
            <div className="toggle-thumb" />
          </div>
        </div>
      </div>

      {/* 회원 탈퇴 */}
      <div className="settings-card settings-card-danger">
        <div className="settings-card-label">회원 탈퇴</div>
        <p className="settings-danger-desc">탈퇴 시 모든 데이터가 삭제되며 복구할 수 없습니다.</p>
        <button className="settings-btn-danger" onClick={() => setShowDeleteModal(true)}>
          회원 탈퇴
        </button>
      </div>

      {/* 탈퇴 확인 모달 */}
      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="modal-box">
            <h3 className="modal-title">정말 탈퇴하시겠어요?</h3>
            <p className="modal-desc">모든 데이터가 삭제되며 복구할 수 없습니다.</p>
            <div className="modal-actions">
              <button
                className="modal-btn-cancel"
                onClick={() => setShowDeleteModal(false)}
                disabled={deleteLoading}
              >
                취소
              </button>
              <button
                className="modal-btn-confirm"
                onClick={handleDeleteAccount}
                disabled={deleteLoading}
              >
                {deleteLoading ? '처리 중...' : '탈퇴하기'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SettingsPage;
