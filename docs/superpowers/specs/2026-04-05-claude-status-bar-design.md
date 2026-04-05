# Claude Status Bar Design Spec

## Overview

Claude Code용 커스텀 Status Line 플러그인. 설치/업데이트까지 지원하는 크로스 플랫폼 지원 Bash 스크립트 기반.

## Requirements

- **플랫폼**: macOS, Linux, Windows (Git Bash)
- **설치 방식**: 직접 복사 (`curl -fsSL <url> | bash`)
- **스크립트 언어**: Python 3 only
- **표시 정보**: 3줄 고정 구조 (디렉토리+브랜치+모델, 컨텍스트+비용, 속도제한)
- **설치 위치**: `~/.claude/plugins/claude-status-bar/`
- **자동 인식**: 설치 시 settings.json 자동 등록
- **버전 관리**: GitHub releases 기반

## Architecture

### Directory Structure

```
~/.claude/plugins/claude-status-bar/
├── README.md
├── install.sh          # 설치 스크립트
├── update.sh           # 업데이트 스크립트
├── uninstall.sh        # 제거 스크립트
├── statusline.py       # 메인 Python 스크립트
└── test/
    └── test_statusline.py
```

### Installation Flow

1. `install.sh` 실행
2. GitHub latest release에서 파일 다운로드
3. `statusline.py` → `~/.claude/plugins/claude-status-bar/statusline.py` 저장
4. `~/.claude/settings.json`에 `statusLine` 설정 자동 등록:
   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "python3 ~/.claude/plugins/claude-status-bar/statusline.py"
     }
   }
   ```
5. 기존 settings.json 병합 (기존 설정 보존)

### Update Flow

1. `update.sh` 실행
2. GitHub latest release 버전 확인
3. 로컬 버전과 비교 후 차이 있으면 다운로드
4. 새 파일로 교체

### Uninstall Flow

1. `uninstall.sh` 실행
2. `settings.json`에서 statusLine 설정 제거
3. `~/.claude/plugins/claude-status-bar/` 디렉토리 삭제

## Status Line Output Format

### Line 1: Workspace Info
```
📁 {directory} 🌿 {branch} 🧠 {model}
```

### Line 2: Context & Cost
```
🧊 {percentage}% [{progress_bar}] 💰 ${cost} (${cost_per_hour}/h)
```

### Line 3: Rate Limits
```
⏳ 5h: {percentage}% [{progress_bar}] 7d: {percentage}% [{progress_bar}]
```

## Data Handling

- JSON stdin 파싱: Python `json` 모듈
- Git 정보: `git` CLI 호출
- 캐싱: `/tmp/statusline-git-cache` (5초 TTL)
- null 처리: `// 0`, `// empty` 폴백

## Error Handling

- git non-repo: branch 정보 없이 디렉토리만 표시
- rate_limits absent: 해당 줄 자체를 표시하지 않음
- Python 미설치: 에러 메시지 출력 후 종료

## Platform Considerations

- Windows (Git Bash): `python3` 대신 `python` 사용 가능성 고려
- Shebang: `#!/usr/bin/env python3` 사용
- 경로: `~/.claude/`는 Windows에서 `C:/Users/{username}/.claude/`

## Testing

- `test/statusline.py`: JSON input을 파싱하여 output 검증
- Mock JSON으로 수동 테스트 가능

## Future Extensibility

- 표시 정보 커스터마이징 (플래그 기반)
- 테마/색상 지원
- 추가 정보 (session duration, lines added/removed 등)
