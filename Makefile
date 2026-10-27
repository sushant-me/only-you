.PHONY: gen demo demo-text scenes report pitch web bench bench-meta smoke test verify all

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

test:
	PYTHONPATH=$(PYTHONPATH) python3 -m unittest discover -s tests -v

verify:
	PYTHONPATH=$(PYTHONPATH) python3 -m onlyyou.cli verify --ledger results/receipts-D.jsonl

all: gen test bench
