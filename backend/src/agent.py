# agent.py
import json
import logging
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# LiveKit agents imports
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("sdr_agent")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)

load_dotenv(".env.local")  # ensure api keys set here

# Path constants
FAQ_FILE = os.environ.get("FAQ_FILE", "company_faq.json")
LEADS_FILE = os.environ.get("LEADS_FILE", "leads.json")


def load_faq(path: str) -> Dict[str, Any]:
    """Load FAQ + metadata from a JSON file. Expected structure:
    {
      "company": "Acme Inc",
      "product_overview": "...",
      "pricing": "...",
      "faq": [
         {"q": "...", "a":"..."},
         ...
      ]
    }
    """
    if not os.path.exists(path):
        logger.warning("FAQ file not found: %s. Using empty template.", path)
        return {"company": "Unknown", "product_overview": "", "pricing": "", "faq": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class Assistant(Agent):
    def __init__(self, faq: Optional[Dict[str, Any]] = None) -> None:
        # Basic SDR instructions (concise + actionable)
        instructions = (
            "You are an SDR voice assistant for the company named dummyAI and product loaded into your FAQ data. "
            "Behave as a helpful, friendly sales rep: greet the visitor warmly, ask what brought them here and what they are working on, "
            "focus the conversation to understand user needs, and collect lead fields naturally. "
            "When a user asks about product, pricing or features, use the FAQ tool `find_faq(question)` to locate answers and reply using only that content. "
            "If the FAQ doesn't contain the answer, say you don't know and offer to collect contact details to follow up. "
            "Collect these lead fields: name, company, email, role, use_case, team_size, timeline (now/soon/later). "
            "When the user signals they are done (e.g., 'thanks', 'that's all', 'i'm done'), summarize the lead verbally and save the collected lead using `save_lead(lead_dict)`. "
            "Keep replies concise and avoid emojis or unusual formatting."
        )
        super().__init__(instructions=instructions)
        self.faq_data = faq or {"company": "Unknown", "product_overview": "", "pricing": "", "faq": []}
        self._lead_buffer: Dict[str, Any] = {}  # in-session lead capture buffer

    # Tools that the LLM/agent can call ------------------------------------------------
    @function_tool
    async def find_faq(self, ctx: RunContext, question: str) -> Dict[str, Any]:
        """
        Simple FAQ lookup tool. Returns:
          { "found": True, "answer": "...", "source_q": "..." } or { "found": False }
        Matching is keyword-based + simple scoring (occurrence count).
        """
        q_lower = question.lower().strip()
        best = None
        best_score = 0

        # search product_overview and pricing first (direct matches)
        candidates = []

        # add explicit faq entries
        for entry in self.faq_data.get("faq", []):
            candidates.append({"q": entry.get("q", ""), "a": entry.get("a", "")})

        # add product_overview and pricing as pseudo-FAQ entries
        if self.faq_data.get("product_overview"):
            candidates.append({"q": "product overview", "a": self.faq_data["product_overview"]})
        if self.faq_data.get("pricing"):
            candidates.append({"q": "pricing", "a": self.faq_data["pricing"]})

        # simple scoring: count of query tokens found in candidate text
        tokens = [t for t in q_lower.replace("?", "").split() if t]
        for c in candidates:
            text = (c.get("q", "") + " " + c.get("a", "")).lower()
            score = sum(text.count(tok) for tok in tokens)
            # small bonus for exact q match
            if q_lower == c.get("q", "").lower().strip():
                score += 5
            if score > best_score:
                best_score = score
                best = c

        # heuristics: require minimal score to accept match
        if best is None or best_score <= 0:
            return {"found": False}
        return {"found": True, "answer": best.get("a", ""), "source_q": best.get("q", "")}

    @function_tool
    async def save_lead(self, ctx: RunContext, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Append a lead record to LEADS_FILE and return summary info."""
        # ensure keys exist
        canonical = {
            "name": lead.get("name"),
            "company": lead.get("company"),
            "email": lead.get("email"),
            "role": lead.get("role"),
            "use_case": lead.get("use_case"),
            "team_size": lead.get("team_size"),
            "timeline": lead.get("timeline"),
            "source": lead.get("source", "voice_agent"),
        }
        # load existing list
        leads = []
        if os.path.exists(LEADS_FILE):
            try:
                with open(LEADS_FILE, "r", encoding="utf-8") as f:
                    leads = json.load(f)
            except Exception:
                leads = []
        leads.append(canonical)
        with open(LEADS_FILE, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
        logger.info("Saved lead: %s", canonical)
        return {"status": "ok", "saved": canonical}

    # Helper to set a lead field in buffer (not a tool: local behavior)
    def set_lead_field(self, key: str, value: Any):
        self._lead_buffer[key] = value

    def get_lead_buffer(self) -> Dict[str, Any]:
        return dict(self._lead_buffer)


# Prewarm (load VAD)
def prewarm(proc: JobProcess):
    logger.info("Prewarming VAD model...")
    proc.userdata["vad"] = silero.VAD.load()


# Entrypoint: builds the session and starts agent -------------------------------------
async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}
    # Load FAQ for the assistant
    faq = load_faq(FAQ_FILE)
    logger.info("Loaded FAQ for company: %s", faq.get("company", "Unknown"))

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage summary: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Create the assistant with FAQ data
    assistant = Assistant(faq=faq)

    # Start the session with the assistant instance
    await session.start(agent=assistant, room=ctx.room, room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()))

    # Connect to the LiveKit room (blocks until stop)
    await ctx.connect()


if __name__ == "__main__":
    # Run worker (use WorkerOptions to configure)
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
