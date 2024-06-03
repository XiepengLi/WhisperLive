from whisper_live.client import TranscriptionClient
import datetime

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import threading

app = FastAPI()

client = TranscriptionClient(
    "127.0.0.1",
    9090,
    lang="en",
    translate=False,
    model="distil-large-v3",  # distil-large-v3
    use_vad=True,
    save_output_recording=True,  # Only used for microphone input, False by Default
    output_recording_filename="./output_recording.wav",  # Only used for microphone input
)


def last_segment(client):
    time.sleep(0.01)
    data = [
        {
            "message": client.last_segments[-1],
            "timestamp": datetime.datetime.now().isoformat(),
        }
    ]

    for item in data:
        yield item


def last_stable_segment(client):
    time.sleep(0.1)
    data = [
        {
            "message": client.stable_segments[-1],
            "timestamp": datetime.datetime.now().isoformat(),
        }
    ]
    for item in data:
        yield item


@app.get("/last_segment")
def last_segment_stream():
    return StreamingResponse(
        last_segment(client.client), media_type="text/event-stream"
    )


@app.get("/last_stable_segment")
def last_stable_segment_stream():
    return StreamingResponse(
        last_stable_segment(client.client), media_type="text/event-stream"
    )


if __name__ == "__main__":
    import uvicorn

    # Start the record in a separate thread
    record_thread = threading.Thread(target=client)
    record_thread.daemon = True
    record_thread.start()

    uvicorn.run(app, host="0.0.0.0", port=8001)