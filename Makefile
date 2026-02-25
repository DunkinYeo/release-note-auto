.PHONY: run setup clean open

# 한번에 실행 — 의존성 자동 설치 후 릴리즈노트 생성
run:
	@echo "📦 Installing dependencies..."
	@pip install -r requirements.txt -q
	@echo "🚀 Generating release notes..."
	@python main.py
	@echo "✅ Done! Check output/ folder."

# 첫 실행 전 환경 세팅 (run에 포함되어 있으므로 보통 불필요)
setup:
	pip install -r requirements.txt

# 생성된 PDF/PNG 결과물 전체 삭제
clean:
	@rm -rf output/pdf/* output/screenshot/*
	@echo "🗑️  output/ cleared."

# 최근 생성된 PDF 바로 열기 (macOS)
open:
	@open output/pdf/*.pdf 2>/dev/null || echo "No PDF found in output/pdf/"
