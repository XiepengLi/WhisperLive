from whisper_live.client import TranscriptionClient, whisper_eager_generator, whisper_full_generator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import threading

app = FastAPI()

client = TranscriptionClient(
    "whisperlive-gpu",
    9090,
    lang="en",
    translate=False,
    model="distil-large-v3",  # distil-large-v3
    use_vad=True,
    save_output_recording=True,  # Only used for microphone input, False by Default
    output_recording_filename="./output_recording.wav",  # Only used for microphone input
)


@app.get("/whisper_eager_stream")
def whisper_eager_stream():
    return StreamingResponse(
        whisper_eager_generator(client.client), media_type="text/event-stream"
    )


@app.get("/whisper_full_stream")
def whisper_full_stream():
    return StreamingResponse(
        whisper_full_generator(client.client), media_type="text/event-stream"
    )


if __name__ == "__main__":
    import uvicorn

    # Start the record in a separate thread
    record_thread = threading.Thread(target=client)
    record_thread.daemon = True
    record_thread.start()

    uvicorn.run(app, host="0.0.0.0", port=8000)