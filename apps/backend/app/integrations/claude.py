import json
from anthropic import Anthropic
from app.core.config import settings

_client: Anthropic | None = None


def get_claude_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=settings.anthropic_api_key)
    return _client


def detect_clips(segments: list[dict], full_text: str) -> list[dict]:
    transcript_lines = "\n".join(
        f"[{s['start']:.1f}s - {s['end']:.1f}s] {s['text']}"
        for s in segments
    ) or full_text

    prompt = (
        "Dado a transcrição a seguir, identifique os 5–10 melhores momentos para Shorts virais. "
        "Para cada momento, retorne:\n"
        "- start_time e end_time (segundos, como números)\n"
        "- title (max 60 chars, em português)\n"
        "- virality_score (inteiro de 0–100)\n"
        "- reasons (array de 2–4 motivos concretos, em português)\n\n"
        "Critérios: gancho nos primeiros 3s, intensidade emocional, conclusão clara, "
        "sem corte no meio de raciocínio. Duração mínima 30s, máxima 90s.\n\n"
        f"Transcrição:\n{transcript_lines}\n\n"
        "Responda SOMENTE com JSON válido, sem markdown:\n"
        '[{"start_time": 0.0, "end_time": 45.0, "title": "...", "virality_score": 80, "reasons": ["..."]}]'
    )

    message = get_claude_client().messages.create(
        model="claude-sonnet-4",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    clips = json.loads(raw)

    result = []
    for clip in clips:
        result.append({
            "start_time": float(clip["start_time"]),
            "end_time": float(clip["end_time"]),
            "title": str(clip.get("title", ""))[:60],
            "virality_score": max(0, min(100, int(clip.get("virality_score", 0)))),
            "reasons": list(clip.get("reasons", []))[:4],
        })

    return sorted(result, key=lambda x: x["virality_score"], reverse=True)
