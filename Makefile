.PHONY: gen demo demo-text scenes report pitch audit web bench bench-meta bench-open smoke test verify all

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

bench-open:
	PYTHONPATH=$(PYTHONPATH) python3 -m onlyyou.cli bench --model open --limit $(or $(LIMIT),10) --out results-open

report:
	python3 tools/md_to_pdf.py docs/report.md docs/report.pdf

pitch:
	python3 tools/md_to_pdf.py docs/pitch.md docs/pitch.pdf --slides

scenes:
	PYTHONPATH=$(PYTHONPATH) python3 -m onlyyou.cli scenes --out results/scene-eval.json

demo-text:
	PYTHONPATH=$(PYTHONPATH) python3 examples/mandate_demo.py

smoke:
	python3 tools/smoke_meta.py

audit:
	ONLYYOU_MODEL=simulated PYTHONPATH=$(PYTHONPATH) python3 tools/audit.py

test:
	ONLYYOU_MODEL=simulated PYTHONPATH=$(PYTHONPATH) python3 -m unittest discover -s tests -v

voice:
	@test -n "$(VOICE)" || (echo "usage: make voice VOICE=narration.wav" && exit 1)
	ffmpeg -y -i docs/demo-3min.mp4 -i "$(VOICE)" -filter_complex "[1:a]aresample=48000,loudnorm=I=-16:TP=-1.5:LRA=11,apad,atrim=0:175[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 160k -movflags +faststart docs/demo-3min-voice.mp4
	@echo "wrote docs/demo-3min-voice.mp4"

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
