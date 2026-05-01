def get_system_mode(url: str) -> str:
    """
    URL 패턴을 분석하여 시스템 실행 모드를 결정합니다.
    """
    url_str = url.lower()
    
    # 1. 게시판(Board) 모드로 판정할 기준 (시연 사이트 위주...)
    board_keywords = [
        "clien.net/service/board", 
        "gall.dcinside.com", 
        "community/list",
        "board.php"
    ]
    
    # 2. 판정 로직
    if any(keyword in url_str for keyword in board_keywords):
        # 만약 URL에 특정 게시글 번호(상세페이지)가 포함되어 있다면 single로 반전 가능
        if "view" in url_str or "article" in url_str:
            return "single"
        return "board"
    
    # 3. 기본값은 single (가장 안전한 탐지 방식)
    return "single"