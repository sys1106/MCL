.PHONY: clean
clean:
	rm -rf *.json
	rm -rf *.out

.PHONY: get_data
get_data:
	python data.py

.PHONY: process_data
process_data:
	python alert.py
	python topology.py

.PHONY: analyze
analyze:
	python mini_ai.py

.PHONY: all
all: clean get_data process_data analyze
