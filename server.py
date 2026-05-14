from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from flask import Flask
from flask_cors import CORS  
import cv2
import numpy as np
from pyzbar import pyzbar
import uvicorn

###app = FastAPI()
app = Flask(__name__)
CORS(app)  

# Allow your React app to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/scan")
async def scan_barcode(file: UploadFile = File(...)):
    cap = cv2.VideoCapture(0)
    
    # Set high definition resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Convert uploaded image to OpenCV format
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Decode barcode
    barcodes = pyzbar.decode(img)
    
    if barcodes:
        # Return the first found barcode
        data = barcodes[0].data.decode("utf-8")
        return {"success": True, "barcode": data}
    
    return {"success": False, "message": "No barcode detected"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)