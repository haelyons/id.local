from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import uvicorn

# Import the existing scoring functions
from score import init, run

# Initialize the models when the server starts
print("Initializing models...")
init()
print("Models initialized successfully!")

app = FastAPI(
    title="Grounded SAM2 Local API",
    description="Local inference endpoint for Grounded SAM2",
    version="1.0.0"
)

# Add CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InferenceRequest(BaseModel):
    caption: str
    images: List[str]  # Base64 encoded images
    box_threshold: Optional[float] = 0.35
    text_threshold: Optional[float] = 0.25
    return_base64_masks: Optional[bool] = False

class InferenceResponse(BaseModel):
    success: bool
    caption: Optional[str] = None
    total_images: Optional[int] = None
    results: Optional[List] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    return {
        "message": "Grounded SAM2 Local API", 
        "status": "running",
        "endpoints": {
            "inference": "/predict",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "models_loaded": True}

@app.post("/predict", response_model=InferenceResponse)
async def predict(request: InferenceRequest):
    try:
        # Convert the request to the format expected by the run function
        raw_data = json.dumps(request.dict())
        
        # Call the existing run function
        result_json = run(raw_data)
        
        # Parse the result and return it
        result = json.loads(result_json)
        
        return InferenceResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/score")  # Alternative endpoint name for compatibility
async def score_endpoint(request: InferenceRequest):
    return await predict(request)

if __name__ == "__main__":
    uvicorn.run(
        "local_server:app",
        host="0.0.0.0",
        port=5001,
        reload=False,
        log_level="info"
    ) 