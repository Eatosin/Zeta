#!/bin/bash
echo "🛠️ Initializing TestForge Environment..."
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "✅ Setup Complete. Run 'source venv/bin/activate' to start."
