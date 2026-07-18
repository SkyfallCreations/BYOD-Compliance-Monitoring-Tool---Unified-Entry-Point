# BYOD Compliance Monitor - Makefile

.PHONY: help install test clean run-full run-sms run-monitor

# Default target
help:
	@echo "BYOD Compliance Monitor - Available Commands:"
	@echo ""
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests"
	@echo "  make run-full     - Run complete extraction"
	@echo "  make run-sms      - Run SMS-only extraction"
	@echo "  make run-monitor  - Run real-time monitoring"
	@echo "  make clean        - Clean up artifacts"
	@echo ""

install:
	@echo "Installing dependencies..."
	python3 -m pip install -r requirements.txt
	@echo "Installation complete!"

test:
	@echo "Running tests..."
	python3 -m pytest tests/

run-full:
	@echo "Running full extraction..."
	python3 main.py --full --report-format html

run-sms:
	@echo "Running SMS extraction..."
	python3 main.py --sms-only

run-contacts:
	@echo "Running contacts extraction..."
	python3 main.py --contacts-only

run-monitor:
	@echo "Starting real-time monitoring..."
	python3 main.py --monitor --duration 60

clean:
	@echo "Cleaning up..."
	rm -rf temp_data/ output/ logs/*.log
	python3 main.py --cleanup
	@echo "Cleanup complete!"

dev-setup: install
	@echo "Setting up development environment..."
	python3 -m pip install pytest black pylint
	@echo "Development environment ready!"
