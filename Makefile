.PHONY: gen demo demo-text scenes brief report pitch audit voice-study latency links web bench bench-meta bench-frontier bench-open smoke test verify all

PYTHONPATH := src

gen:
	PYTHONPATH=$(PYTHONPATH) python3 -m onlyyou.cli gen --out data/scenarios.jsonl

demo:
	PYTHONPATH=$(PYTHONPATH) python3 -m onlyyou.cli demo

web:
	PYTHONPATH=$(PYTHONPATH) python3 -m onlyyou.cli web --port 8000

bench:
	PYTHONPATH=$(PYTHONPATH) python3 -m onlyyou.cli bench --model simulated --out results

bench-meta:
	PYTHONPATH=$(PYTHONPATH) python3 -m onlyyou.cli bench --model meta --out results-real

bench-frontier:
	PYTHONPATH=$(PYTHONPATH) python3 -m onlyyou.cli bench --model frontier --limit $(or $(LIMIT),8) --out results-frontier

bench-open:
	PYTHONPATH=$(PYTHONPATH) python3 -m onlyyou.cli bench --model open --limit $(or $(LIMIT),10) --out results-open

brief:
	python3 tools/md_to_pdf.py docs/brief.md docs/brief.pdf

report:
	python3 tools/md_to_pdf.py docs/report.md docs/report.pdf

pitch:
	python3 tools/md_to_pdf.py docs/pitch.md docs/pitch.pdf --slides

scenes:
	PYTHONPATH=$(PYTHONPATH) python3 -m onlyyou.cli scenes --out results/scene-eval.json

demo-text:
	PYTHONPATH=$(PYTHONPATH) python3 examples/mandate_demo.py

voice-study:
	PYTHONPATH=$(PYTHONPATH) python3 tools/voice_study.py --owner data/voice-study/owner --impostors data/voice-study/impostors

latency:
	PYTHONPATH=src python3 tools/latency.py

links:
	python3 tools/check_links.py

smoke:
	python3 tools/smoke_meta.py

audit:
	ONLYYOU_MODEL=simulated PYTHONPATH=$(PYTHONPATH) python3 tools/audit.py

test:
	ONLYYOU_MODEL=simulated ONLYYOU_SKIP_BROWSER=1 PYTHONPATH=$(PYTHONPATH) python3 -m unittest discover -s tests -v

voice:
	@test -n "$(VOICE)" || (echo "usage: make voice VOICE=narration.wav" && exit 1)
	python3 tools/mux_voice.py "$(VOICE)"

preflight:
	python3 tools/preflight.py

smoke-web:
	PYTHONPATH=$(PYTHONPATH) python3 tools/smoke_web.py

judge:
	@echo "ONLY YOU - judge check"
	@python3 --version
	@ONLYYOU_MODEL=simulated PYTHONPATH=$(PYTHONPATH) python3 -m unittest discover -s tests -q
	@PYTHONPATH=$(PYTHONPATH) python3 tools/smoke_web.py
	@AUDIT_SKIP_GIT_CLEAN=1 PYTHONPATH=$(PYTHONPATH) python3 tools/audit.py
	@echo ""
	@echo "Demo:  make web   then open  http://127.0.0.1:8000/?script=full&fakecam=1"
	@echo "Video: docs/demo-3min.mp4   Report: docs/report.pdf   Page: docs/index.html"

verify:
	PYTHONPATH=$(PYTHONPATH) python3 -m onlyyou.cli verify --ledger results/receipts-D.jsonl

all: gen test bench

docker:
	docker build -t only-you-demo .

docker-run:
	docker run --rm -p 8000:8000 --name only-you-demo only-you-demo
