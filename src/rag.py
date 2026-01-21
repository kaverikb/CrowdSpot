import requests
import os
from dotenv import load_dotenv

load_dotenv()

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
        deviation_text = self._deviation_label(z_score)

        prompt = f"""Zone: {zone}
Observed count: {int(person_count)}
Density: {density_level}
Deviation: {deviation_text}

Write a 1-2 sentence summary for patrol supervisor. Be factual, calm, operational.
Output ONLY the summary text."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 50
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
                return f"Error {response.status_code}"

        except Exception as e:
            return f"LLM unavailable: {str(e)}"
