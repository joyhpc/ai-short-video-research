"""Allow running quality gate as: python -m src.quality_gate"""
import sys
from . import main
sys.exit(main())
