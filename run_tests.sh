#!/bin/bash
# Script to run tests for the Mergington High School Activities API

echo "Running FastAPI tests with coverage..."

# Run pytest with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html -v

echo ""
echo "Test run completed!"
echo "HTML coverage report generated in htmlcov/ directory"