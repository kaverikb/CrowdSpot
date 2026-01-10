import requests
import os


class RAGSummary:
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not provided")

        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "deepseek/deepseek-chat"

    def _deviation_label(self, z_score):
        """
        Convert numeric z-score into human-readable deviation.
        Raw z-scores are not suitable for operator-facing text.
        """
        z = abs(z_score)

        if z < 1:
            return "within normal range"
        elif z < 3:
            return "moderately above normal"
        else:
            return "significantly above normal"

    def generate_summary(
        self,
        zone,
        person_count,
        density_level,
        baseline_mean,
        baseline_std,
        z_score
    ):
        """
        Generate a human-readable crowd summary for police operations.
        Uses interpretable signals only.
        """

        deviation_text = self._deviation_label(z_score)

        prompt = f"""
Zone: {zone}

Observed people count: {int(person_count)}
Crowd density level (PRIMARY INDICATOR): {density_level}
Deviation from historical baseline (SECONDARY CONTEXT): {deviation_text}

IMPORTANT INSTRUCTIONS:
- Treat the density level as the authoritative assessment
- Deviation text provides context only and must not override the density level
- If density level is LOW, do NOT describe the situation as elevated or high
- If density level is LOW, avoid phrases like "significant" or "requires attention"


Task:
Write a 2–3 sentence summary for a patrol supervisor.

Rules:
- Be factual and calm
- Do NOT infer intent (no protest, no panic, no criminal motive)
- Compare current conditions to what is normally observed
- Avoid dramatic or alarmist language
- Focus on operational relevance only

IMPORTANT:
- Output ONLY the summary text
- Do NOT include explanations, bullet points, labels, headings, word counts, or self-evaluation
- Do NOT mention rules, guidelines, or why the summary is good
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"LLM Error {response.status_code}: {response.text}"

        except Exception as e:
            return f"Request failed: {str(e)}"
