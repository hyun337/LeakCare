export const fetchDashboardData = async () => {
  // 실제 API 호출 대신 가짜 데이터로 테스트 진행 
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        summary: {
          detectCount: 128,
          deleteRequestCount: 45,
          inProgressCount: 12,
        },
        recentLogs: [
          { id: 1, target: "https://sns-platform.com/v/asdf123", status: "분석중", date: "2026-03-17 09:20" },
          { id: 2, target: "https://video-site.net/watch?v=xyz", status: "완료", date: "2026-03-16 22:15" },
          { id: 3, target: "https://community.org/post/789", status: "오류", date: "2026-03-16 18:05" },
          { id: 4, target: "https://blog.com/article/001", status: "완료", date: "2026-03-16 14:30" },
          { id: 5, target: "https://tube.com/short/555", status: "완료", date: "2026-03-15 20:00" },
        ],
      });
    }, 500);
  });
};