import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Any
from loguru import logger
# IMPORT SENTINEL LOGIC
from src.ml.anomaly_detection import AnomalyDetector 

class EdgeCaseDetector:
    """
    Hybrid Physics-ML Engine.
    Combines IsolationForest (ML) with Sentinel Z-Scores (Physics).
    """

    def __init__(self, contamination=0.1):
        self.ml_model = IsolationForest(contamination=contamination, random_state=42)
        # Initialize Sentinel Engine
        self.physics_engine = AnomalyDetector(threshold=2.5) 
        logger.info("Engines Initialized: IsolationForest + Sentinel Z-Score")

    def analyze_complexity(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not requirements:
            return []

        # 1. Feature Extraction
        features = []
        lengths = [] # We will track text length for Z-Score analysis
        
        for req in requirements:
            text = req.get("text", "")
            length = len(text)
            lengths.append(length)
            
            features.append([
                length,
                text.count(",") + text.count("and"),
                1 if "must" in text.lower() else 0,
                1 if "user" in text.lower() else 0
            ])

        X = np.array(features)

        # 2. Run ML Model (Isolation Forest)
        ml_predictions = self.ml_model.fit_predict(X)
        
        # 3. Run Sentinel Physics Engine (Z-Score on Length/Complexity)
        physics_anomalies = self.physics_engine.detect(lengths)

        # 4. Synthesize Results
        analyzed_reqs = []
        for i, req in enumerate(requirements):
            # It is an edge case if ML says so OR Physics says so
            is_ml_anomaly = ml_predictions[i] == -1
            is_physics_anomaly = physics_anomalies[i]
            
            risk_source = []
            if is_ml_anomaly: risk_source.append("ML_Pattern")
            if is_physics_anomaly: risk_source.append("Physics_ZScore")

            req["risk_analysis"] = {
                "is_edge_case": is_ml_anomaly or is_physics_anomaly,
                "risk_sources": risk_source,
                "risk_level": "CRITICAL" if (is_ml_anomaly and is_physics_anomaly) else "HIGH" if is_physics_anomaly else "NORMAL"
            }
            analyzed_reqs.append(req)

        return analyzed_reqs
