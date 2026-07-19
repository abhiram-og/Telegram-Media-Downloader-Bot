# 🎬 Telegram Media Downloader Bot

🤖 **Live Bot:** [@VidExtractBot](https://t.me/VidExtractBot)

A production-ready Telegram bot built with **FastAPI** that downloads videos from **X (Twitter)** posts and sends them back as Telegram video messages.

Designed with Clean Architecture for easy extensibility to Instagram, YouTube, Reddit, and TikTok.

---

## ✨ Features

- **X / Twitter video downloads** — Send a post URL, get the video back
- **Clean Architecture** — Separation of concerns with services, downloaders, and utilities
- **Extensible design** — Add new platforms by creating a downloader class and registering it
- **Background processing** — Downloads run asynchronously so the webhook responds immediately
- **Automatic cleanup** — Temp files are deleted after upload and on startup
- **Error handling** — User-friendly messages for all error cases
- **Health check** — Built-in `/health` endpoint for monitoring

---

## 📁 Project Structure

```
Media-downloader/
│
├── app/
│   ├── main.py                  # FastAPI application entry point
│   │
│   ├── core/
│   │   ├── config.py            # Pydantic Settings configuration
│   │   ├── logger.py            # Centralized logging
│   │   └── constants.py         # Platform patterns & message templates
│   │
│   ├── api/
│   │   └── webhook.py           # POST /webhook endpoint
│   │
│   ├── downloaders/
│   │   ├── base.py              # Abstract BaseDownloader + exceptions
│   │   ├── twitter.py           # TwitterDownloader (yt-dlp)
│   │   └── factory.py           # DownloaderFactory registry
│   │
│   ├── services/
│   │   ├── telegram_service.py  # Telegram Bot API wrapper
│   │   ├── download_service.py  # Download orchestration
│   │   └── cleanup_service.py   # File cleanup
│   │
│   └── utils/
│       ├── validators.py        # URL validation & platform detection
│       └── file_utils.py        # File system helpers
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Installation

### Prerequisites

- Python 3.12+
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- ffmpeg installed (for yt-dlp video merging)

### Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd Media-downloader

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## ⚙️ Environment Variables

Create a `.env` file in the project root (see `.env.example`):

| Variable          | Required | Default | Description                                    |
|-------------------|----------|---------|------------------------------------------------|
| `BOT_TOKEN`       | ✅       | —       | Telegram bot API token from @BotFather         |
| `WEBHOOK_SECRET`  | ✅       | —       | Secret to verify webhook requests              |
| `WEBHOOK_URL`     | ✅       | —       | Public URL for the webhook (e.g. ngrok URL)    |
| `TEMP_DIRECTORY`  | ❌       | `temp`  | Directory for temporary downloaded files       |
| `MAX_FILE_SIZE_MB`| ❌       | `100`   | Maximum allowed download file size in MB       |

---

## 🏃 Running Locally

### 1. Start the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Expose with ngrok (for development)

```bash
ngrok http 8000
```

### 3. Set the Telegram webhook

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://<YOUR_NGROK_URL>/webhook", "secret_token": "<YOUR_WEBHOOK_SECRET>"}'
```

### 4. Verify the webhook

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

### 5. Test it

Open your bot in Telegram and send a Twitter/X post URL!

---

## 🚢 Deployment Notes

- Use a reverse proxy (Nginx, Caddy) with HTTPS in production
- Set `WEBHOOK_URL` to your public HTTPS domain
- Telegram requires HTTPS for webhooks
- Consider using a process manager (systemd, supervisord) in production
- The bot uses Telegram's 50 MB upload limit — larger videos will be rejected gracefully

---

## 🗺️ Future Roadmap

| Platform   | Status      |
|------------|-------------|
| X/Twitter  | ✅ Supported |
| Instagram  | 🔜 Planned   |
| YouTube    | 🔜 Planned   |
| Reddit     | 🔜 Planned   |
| TikTok     | 🔜 Planned   |

### Adding a New Platform

1. Create `app/downloaders/newplatform.py`:
   ```python
   class NewPlatformDownloader(BaseDownloader):
       @property
       def platform_name(self) -> str:
           return "NewPlatform"

       async def download(self, url: str, output_dir: Path) -> Path:
           # Implementation here
           ...

       async def validate_url(self, url: str) -> bool:
           # URL validation here
           ...
   ```

2. Add the URL pattern in `app/core/constants.py`:
   ```python
   PLATFORM_PATTERNS["newplatform"] = re.compile(r"https?://...")
   ```

3. Register in `app/downloaders/factory.py`:
   ```python
   def _register_defaults(self) -> None:
       self.register("twitter", TwitterDownloader())
       self.register("newplatform", NewPlatformDownloader())
   ```