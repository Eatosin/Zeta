from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.core.llm_engine import LLMEngine
from src.ml.edge_case_detector import EdgeCaseDetector
from src.core.code_generator import SeleniumGenerator
from src.api.models import GenerateRequest, TestSuiteResponse, CodeGenRequest, CodeResponse
import uvicorn
import uuid
import os
from loguru import logger

# --- LIFESPAN MANAGER (2026 Best Practice) ---
# We load heavy ML models only when the server starts, not on import.
ml_resources = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("⚡ System Startup: Loading AI Engines...")
    try:
        ml_resources["llm"] = LLMEngine()
        ml_resources["ml"] = EdgeCaseDetector()
        ml_resources["codegen"] = SeleniumGenerator()
        logger.info("✅ Engines Online.")
    except Exception as e:
        logger.critical(f"❌ Engine Startup Failed: {e}")
        raise e
    yield
    # Cleanup code could go here
    ml_resources.clear()
    logger.info("🛑 System Shutdown.")

# --- APP CONFIG ---
app = FastAPI(
    title="TestForge AI API",
    version="1.0.0",
    lifespan=lifespan
)

# Security: CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock this to the Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "active", 
        "engines_loaded": list(ml_resources.keys())
    }

@app.post("/generate", response_model=TestSuiteResponse)
async def generate_tests(request: GenerateRequest):
    logger.info(f"Processing generation request ({len(request.requirements_text)} chars)")
    
    if "llm" not in ml_resources:
        raise HTTPException(status_code=503, detail="AI Engines not ready")

    try:
        # 1. Generate Raw Tests
        raw_tests = await ml_resources["llm"].generate_test_cases(request.requirements_text)
        
        # 2. Apply Physics/ML Analysis
        # Map fields for the detector
        for test in raw_tests:
            # Create synthetic text field for analysis if missing
            if "text" not in test:
                test["text"] = f"{test.get('title', '')} {' '.join(test.get('steps', []))}"
            
        analyzed_tests = await ml_resources["ml"].analyze_complexity(raw_tests)
        
        return TestSuiteResponse(
            suite_id=str(uuid.uuid4()),
            test_cases=analyzed_tests,
            meta={"source": "Gemini 2.5", "ml_validation": True}
        )
        
    except Exception as e:
        logger.error(f"Generation logic failed: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error")

@app.post("/codegen", response_model=CodeResponse)
async def generate_code(request: CodeGenRequest):
    if "codegen" not in ml_resources:
        raise HTTPException(status_code=503, detail="Codegen Engine not ready")
        
    try:
        code = ml_resources["codegen"].generate_test_script(request.test_plan)
        return CodeResponse(
            filename=f"test_{uuid.uuid4().hex[:8]}.py",
            python_code=code
        )
    except Exception as e:
        logger.error(f"Codegen failed: {e}")
        raise HTTPException(status_code=500, detail="Code generation failed")

if __name__ == "__main__":
    # Robust port handling for Cloud
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=port, reload=True)
