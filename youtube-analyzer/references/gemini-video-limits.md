# Gemini Video Understanding - Limits & Optimization

## API Limits

### Video Duration
| Model | Max Duration | Notes |
|-------|--------------|-------|
| gemini-3-pro-preview | ~1 hour | Best quality |
| gemini-3-flash | ~1 hour | Faster, cheaper |
| gemini-2.5-flash | ~1 hour | Alternative |

### Rate Limits (Free Tier)
- **RPM (Requests Per Minute)**: 15
- **TPM (Tokens Per Minute)**: 1,000,000
- **RPD (Requests Per Day)**: 1,500

### Token Costs
Video processing consumes significant tokens:
- Short video (~1 min): ~1,000-2,000 tokens
- Medium video (~10 min): ~10,000-20,000 tokens
- Long video (~30+ min): ~50,000+ tokens

## Supported URL Formats

```
✅ Supported:
- https://www.youtube.com/watch?v=VIDEO_ID
- https://youtu.be/VIDEO_ID
- https://www.youtube.com/embed/VIDEO_ID
- https://www.youtube.com/shorts/VIDEO_ID
- https://www.youtube.com/v/VIDEO_ID

❌ Not Supported:
- https://vimeo.com/...
- https://www.tiktok.com/...
- https://example.com/video.mp4
- Any non-YouTube URL
```

## Video Access Requirements

| Video Type | Supported | Notes |
|------------|-----------|-------|
| Public | ✅ | Works |
| Unlisted | ✅ | Works (if you have the URL) |
| Private | ❌ | Cannot access |
| Age-restricted | ❌ | Requires login |
| Members-only | ❌ | Requires subscription |
| Geo-blocked | ⚠️ | May fail depending on Google's servers |
| Deleted | ❌ | Cannot access |

## Optimization Strategies

### For Long Videos
1. **Ask for specific timestamps**: "What happens in the first 5 minutes?"
2. **Request summaries**: "Summarize in bullet points"
3. **Chunked analysis**: Make multiple requests for different time ranges

### For Rate Limits
1. Add delays between requests: `time.sleep(4)` for free tier
2. Batch prompts in single request when possible
3. Use flash model for less critical analysis

### For Better Results
1. **Be specific**: "Describe the gameplay mechanics" > "What's in the video"
2. **Ask for structure**: "List the main topics covered"
3. **Include context**: "As a game analyst, evaluate..."

## Alternative Approaches

When Gemini YouTube analysis doesn't work:

### 1. Transcript Extraction (Text Only)
```bash
pip install youtube-transcript-api
```
```python
from youtube_transcript_api import YouTubeTranscriptApi
transcript = YouTubeTranscriptApi.get_transcript('VIDEO_ID')
```

### 2. Download + Frame Extraction (Visual)
```bash
# Download
yt-dlp -f "best[height<=720]" "URL" -o video.mp4

# Extract frames
ffmpeg -i video.mp4 -vf "fps=0.1" frames/frame_%04d.jpg
```

### 3. File API Upload (Non-YouTube)
```python
from google import genai

client = genai.Client(api_key=API_KEY)
video_file = client.files.upload(file="video.mp4")
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=[video_file, "Describe this video"]
)
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Cannot fetch content from URL` | Private/restricted video | Use public video |
| `RESOURCE_EXHAUSTED` | Rate limit hit | Wait and retry |
| `INVALID_ARGUMENT` | Bad URL format | Check URL validity |
| `DEADLINE_EXCEEDED` | Video too long/timeout | Try shorter video |
| `NoneType object` | API response issue | Retry or check SDK version |

## Model Comparison for Video

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| gemini-3-pro-preview | Slow | Best | High | Deep analysis |
| gemini-3-flash | Fast | Good | Low | Quick summaries |
| gemini-2.5-pro | Medium | Excellent | Medium | Balanced |
| gemini-2.5-flash | Fastest | Good | Lowest | Bulk processing |
