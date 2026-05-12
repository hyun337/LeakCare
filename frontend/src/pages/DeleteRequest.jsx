//삭제 요청서 
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { getRemovalText, getFullReport } from "../api/reportApi";
import "../styles/DeleteRequest.css";

export default function DeleteRequest() {
  const { reportId } = useParams();

  const [report, setReport] = useState(null);
  const [mailText, setMailText] = useState("");
  const [activeTab, setActiveTab] = useState("ko");
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError("");

        const [reportRes, textRes] = await Promise.all([
          getFullReport(reportId),
          getRemovalText(reportId),
        ]);

        if (reportRes.ok) setReport(reportRes.data);
        if (textRes.ok) setMailText(textRes.data.text || "");

        if (!reportRes.ok && !textRes.ok) {
          setError("삭제 요청서를 불러오는데 실패했습니다.");
        }

      } catch (err) {
        console.error("삭제 요청서 로딩 실패:", err);
        setError("삭제 요청서를 불러오는데 실패했습니다.");
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [reportId]);

  const handleCopy = () => {
    navigator.clipboard.writeText(mailText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleMailto = () => {
    const subject = encodeURIComponent("불법 유출 콘텐츠 삭제 요청 / Content Removal Request");
    const body = encodeURIComponent(mailText);
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
  };

  const formattedDate = report?.created_at
    ? new Date(report.created_at).toLocaleString("ko-KR", { timeZone: "Asia/Seoul" })
    : "-";

  if (loading) {
    return (
      <div className="dr-loading">
        <div className="dr-spinner" />
        <p>삭제 요청 메일을 생성하고 있습니다...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dr-loading">
        <p style={{ color: "red" }}>{error}</p>
      </div>
    );
  }

  return (
    <div className="dr-page">
      <div className="dr-header">
        <h1 className="dr-title">삭제 요청서</h1>
        <p className="dr-subtitle">AI가 생성한 삭제 요청 메일입니다. 복사 후 직접 발송해주세요.</p>
      </div>

      {report && (
        <div className="dr-card">
          <p className="dr-card-label">탐지 요약</p>
          <div className="dr-meta-row">
            <div className="dr-meta-item">
              <span className="dr-meta-key">게시 URL</span>
              <span className="dr-meta-val dr-meta-val--link">{report.url}</span>
            </div>
            <div className="dr-meta-item">
              <span className="dr-meta-key">상태</span>
              <span className="dr-meta-val">{report.status}</span>
            </div>
            <div className="dr-meta-item">
              <span className="dr-meta-key">수집 일시</span>
              <span className="dr-meta-val">{formattedDate}</span>
            </div>
          </div>
        </div>
      )}

      <div className="dr-card">
        <div className="dr-mail-box">
          <textarea
            className="dr-mail-text"
            value={mailText}
            onChange={(e) => setMailText(e.target.value)}
            rows={16}
          />
        </div>

        <div className="dr-actions">
          <button className="dr-btn dr-btn--primary" onClick={handleCopy}>
            {copied ? "✓ 복사됨" : "클립보드에 복사"}
          </button>
          <button className="dr-btn dr-btn--secondary" onClick={handleMailto}>
            메일 앱으로 열기
          </button>
        </div>

        <div className="dr-note">
          직접 발송 기능은 제공되지 않습니다. 복사 후 이메일 클라이언트에서 발송해주세요.
          IP·위치 정보는 ip-api.com 기반으로 정확도에 한계가 있을 수 있습니다.
        </div>
      </div>
    </div>
  );
}
