# Growtrics AI Video Demo

A project that simulates the automated process of generating educational videos (AI-generated educational videos). The system allows users to input an educational topic, after which it automatically generates a lesson plan and explanations using AI.

## ⚠️ Known Limitations
In the current version, the system **only supports generating scripts and voiceovers (audio/TTS)**.
The feature to generate visual illustrations (visuals/images) for the video is **not yet implemented**. The final output file focuses primarily on the script and narration audio.

## 🏗 Architecture Note

### Job Lifecycle
When a user submits a query, the API validates it and creates a **Video Job** in the database with a `queued` status. The API responds immediately with a Job ID. An asynchronous background worker picks up the job from the queue and orchestrates the generation process. The job transitions through various stages (e.g., `resolving_concept`, `planning_lesson`, `generating_audio`, `rendering_video`), updating its status and progress in the database. Clients poll the API using the Job ID to receive real-time status updates and event logs.

### Persistence / Artifact Boundary
State and metadata are strictly separated from heavy media files.
- **Database (SQLite/PostgreSQL):** Stores job states, pipeline events, lesson plans, and lightweight metadata (JSON).
- **Artifact Storage (Local Filesystem):** Large generated media files (e.g., scene audios, subtitles, and the final `.mp4` video) are persisted directly to the local filesystem inside an `artifacts/` directory. The database only stores relative paths and completion statuses for these files.

### AI / Video-Generation Boundary
The pipeline logically divides cognitive generation and deterministic media rendering:
- **AI Boundary:** Involves LLM calls for structured lesson planning and scriptwriting, followed by TTS (Text-to-Speech) provider calls for voiceover generation. These tasks are inherently non-deterministic and prone to external API latency.
- **Video-Generation Boundary:** Once scripts and audio are finalized and validated, the process hands over to a deterministic renderer (like FFmpeg). The renderer simply composites the locally cached audio, generated subtitles, and static/fallback visuals into the final video, isolating rendering failures from AI generation steps.

## 1. Prerequisites
- **Python:** Version 3.10 or higher is recommended.
- **FFmpeg:** Must be installed on your machine and added to the operating system's `PATH` environment variable. This is mandatory for the system to combine audio and render the final media file.

## 2. Installation Guide
The project uses a pre-configured SQLite database, so you don't need to install Docker or PostgreSQL.

1. Clone the repository and open a terminal at the root directory.
2. Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```
3. Create the environment configuration file by copying from the example file:
   ```bash
   cp .env.example .env
   ```
   *(On Windows PowerShell, you can manually copy/paste the file and rename it to `.env`)*

## 3. Running the System

Start the FastAPI server (the asynchronous worker will automatically start alongside the server):
```bash
uvicorn app.main:app --reload
```

## 4. Testing the Demo
Once the terminal indicates a successful startup, you can access:

- **Client Demo Interface:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **API Documentation (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

**How to test the workflow:**
1. Open the Client Demo Interface using the link above.
2. Enter a supported question in the database. Ex: `"How does the pH scale work?"`
3. Click the **Generate Video** button and monitor the Progress Bar.
4. The system will run the following steps in the background: *Lesson Planning -> TTS Processing (Audio) -> File Rendering*.