# Claude Status Bar

Claude Code용 커스텀 Status Line 플러그인.

## 표시 정보

3줄 구조로 다음과 같은 정보를 표시합니다:

| 줄 | 내용 | 예시 |
|---|---|---|
| 1 | 디렉토리, 브랜치, 모델 | 📁 my-project 🌿 main 🧠 Opus |
| 2 | 컨텍스트 사용량 + 비용 | 🧊 10% [██████████] 💰 $1.25 ($0.50/h) |
| 3 | 속도 제한 (5시간/7일) | ⏳ 5h: 21% [██░░░░░░░░] 7d: 44% [████░░░░░░] |

## 설치

```bash
curl -fsSL https://raw.githubusercontent.com/PriuS2/ClaudeCode-StatusLine/main/install.sh | bash
```

## 업데이트

```bash
curl -fsSL https://raw.githubusercontent.com/PriuS2/ClaudeCode-StatusLine/main/update.sh | bash
```

## 제거

```bash
curl -fsSL https://raw.githubusercontent.com/PriuS2/ClaudeCode-StatusLine/main/uninstall.sh | bash
```

## 요구사항

- Python 3
- Claude Code CLI

## 수동 테스트

```bash
echo '{"model":{"display_name":"Opus"},"context_window":{"used_percentage":25},"cost":{"total_cost_usd":1.25,"total_duration_ms":3600000},"workspace":{"current_dir":"/test"}}' | python3 statusline.py
```

## 라이선스

MIT