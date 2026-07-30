#!/bin/bash
echo Building Atlas...
pip install -r requirements-dev.txt
pytest tests/ -v
