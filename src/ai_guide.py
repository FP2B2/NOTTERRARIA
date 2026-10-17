"""
Asynchronous, non-blocking bridge to Ollama (Gemma 4 12B).
Injects live player inventory, biome depth, and world status into prompts
and streams tokens into a thread-safe queue for the in-game dialogue UI.
"""

import json
import threading
import queue
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from .config import OLLAMA_HOST, OLLAMA_MODEL


class AIGuideBridge:
    def __init__(self, host: str = OLLAMA_HOST, model: str = OLLAMA_MODEL):
        self.host = host
        self.model = model
        self.dialogue_queue = queue.Queue()
        self.is_thinking = False
        self.last_full_response = ""
        self.active_thread: Optional[threading.Thread] = None

    def query_guide_async(self, player_context: Dict[str, Any], question: str):
        """Dispatches an asynchronous query to Gemma 4 12B without blocking the game loop."""
        if self.is_thinking:
            return  # Already processing a request

        self.is_thinking = True
        self.dialogue_queue = queue.Queue()  # Reset queue
        self.last_full_response = ""

        self.active_thread = threading.Thread(
            target=self._worker,
            args=(player_context, question),
            daemon=True,
        )
        self.active_thread.start()

    def _worker(self, ctx: Dict[str, Any], question: str):
        system_prompt = (
            "You are the Guide in a 2D survival sandbox world inspired by Terraria. "
            "Speak in concise, atmospheric fantasy dialogue (1 to 3 short sentences max). "
            "You are fully aware of what the player is carrying, their current health, "
            "their depth layer, and the time of day. "
            "Provide helpful survival tips, crafting recipes, or lore according to their current gear. "
            "Never break character. Never output conversational filler like 'Sure!'."
        )

        user_content = (
            f"=== CURRENT PLAYER STATUS ===\n"
            f"Layer: {ctx.get('stratum', 'Surface')}\n"
            f"Time of Day: {ctx.get('time_of_day', 'Day')}\n"
            f"Health: {ctx.get('health', 100)}/{ctx.get('max_health', 100)}\n"
            f"Inventory: {ctx.get('inventory_summary', 'Empty')}\n"
            f"Question: {question}\n"
            f"Guide's advice:"
        )

        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\n{user_content}",
            "stream": True,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 120,  # Keep responses crisp and punchy
            },
        }

        url = f"{self.host}/api/generate"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                for line in response:
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        token = chunk.get("response", "")
                        if token:
                            self.last_full_response += token
                            self.dialogue_queue.put(token)
                        if chunk.get("done", False):
                            break
        except urllib.error.URLError as e:
            fallback = (
                "The stars are veiled in mist... Chop trees for shelter before dusk, "
                "and craft a Work Bench to unlock new recipes."
            )
            for ch in fallback:
                self.dialogue_queue.put(ch)
            self.last_full_response = fallback
        finally:
            self.dialogue_queue.put(None)  # Sentinel indicates completion
            self.is_thinking = False

    def poll_token(self) -> Optional[str]:
        """Returns the next streamed token from Gemma 4, or None if queue is empty or complete."""
        try:
            return self.dialogue_queue.get_nowait()
        except queue.Empty:
            return ""
