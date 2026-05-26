import os
import httpx  # Add this to handle outgoing HTTP requests
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import zxingcpp 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Grab your Node.js Main App Domain URL from environment variables
# e.g., MAIN_APP_URL = "https://your-main-node-app.vercel.app"
MAIN_APP_URL = os.getenv("MAIN_APP_URL", "https://quickscannerver2.vercel.app") 

@app.get("/")
def read_root():
    return {"message": "Barcode API is running on Vercel!"}
    
@app.post("/scan")
async def scan_barcode(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return {"success": False, "message": "Invalid image file"}

        results = zxingcpp.read_barcodes(img)
        
        if results:
            barcode_value = results[0].text
            
            # 🚀 FORWARD THE RESULT TO YOUR NODE.JS EXPRESS LOG ENDPOINT
            async with httpx.AsyncClient() as client:
                try:
                    await client.post(
                        f"{MAIN_APP_URL}/api/scan/log",
                        json={"barcode": barcode_value, "source": "python-scanner"}
                    )
                except Exception as log_err:
                    print(f"Failed to broadcast to Node server: {log_err}")

            return {"success": True, "barcode": barcode_value}
        
        return {"success": False, "message": "No barcode detected"}
    except Exception as e:
        return {"success": False, "message": str(e)}
