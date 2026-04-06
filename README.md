# Claude Status Bar

Claude Code용 커스텀 Status Line 플러그인.

## 표시 정보

3줄 구조로 다음과 같은 정보를 표시합니다:

| 줄 | 내용 | 예시 |
|---|---|---|
| 1 | 디렉토리, 브랜치, 모델 | 📁 my-project 🌿 main 🧠 Opus |
| 2 | 컨텍스트 사용량 | 🧊 10% (15,000/200,000) [██░░░░░░░░] |
| 3 | API 사용량 (5시간/7일) + 리셋시간 | 🌐 5h: 4,500/4,500 (100%) [██████████] 7d: 40,000/45,000 (89%) [███████░░░] (R:2h30m/165d) |
| 4 | MiniMax API 잔여량 (선택) | MiniMax-M2.7 모델 사용 시 자동 표시 |

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
echo '{"model":{"display_name":"MiniMax-M2.7"},"context_window":{"used_percentage":16,"context_window_size":200000,"current_usage":{"input_tokens":32000,"output_tokens":5000}},"cost":{"total_cost_usd":0.00,"total_duration_ms":3600000},"workspace":{"current_dir":"/test"}}' | python3 statusline.py
```

## 라이선스

MIT