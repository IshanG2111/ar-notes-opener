
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import uvicorn
import cv2
import numpy as np
import base64
import json

app = FastAPI(title="AR Notes Web", description="Web-based Augmented Reality Notes System", version="1.0.0")

# Mount assets directory to serve files
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Lazily import the WebGestureSystem so the server can start without mediapipe
    try:
        from web_gesture_system import WebGestureSystem
    except Exception as e:
        # If import fails (e.g., mediapipe not installed), notify client and close
        print(f"Failed to import WebGestureSystem: {e}")
        await websocket.send_json({"error": "Server missing optional dependency for gesture processing."})
        try:
            await websocket.close()
        except:
            pass
        return

    # Create a new gesture system instance for this session
    gesture_system = WebGestureSystem()
    print(f"New session started: {id(gesture_system)}")

    try:
        while True:
            data = await websocket.receive_text()

            # Decode base64 image
            # Data format: "data:image/jpeg;base64,....."
            if "," in data:
                try:
                    header, encoded = data.split(",", 1)
                    image_data = base64.b64decode(encoded)
                    nparr = np.frombuffer(image_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    if frame is not None:
                        # Process frame
                        processed_frame, action = gesture_system.process_frame(frame)

                        # Encode back to base64
                        _, buffer = cv2.imencode('.jpg', processed_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                        processed_base64 = base64.b64encode(buffer).decode('utf-8')

                        # Prepare response
                        response = {
                            "image": f"data:image/jpeg;base64,{processed_base64}",
                            "action": action
                        }

                        await websocket.send_json(response)
                    else:
                        await websocket.send_json({"error": "Failed to decode frame"})
                except Exception as e:
                    print(f"Frame processing error: {e}")
                    await websocket.send_json({"error": "Frame processing error"})
            else:
                 await websocket.send_json({"error": "Invalid data format"})

    except WebSocketDisconnect:
        print(f"Client disconnected: {id(gesture_system)}")
    except Exception as e:
        print(f"Connection error: {e}")
        try:
            await websocket.close()
        except:
            pass

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
