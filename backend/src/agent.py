import asyncio
import json
import logging
import os
import random
from datetime import datetime
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    RoomInputOptions,
    WorkerOptions,
    cli,
    function_tool,
    tokenize,
)

from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# ---------------------------------------------------------
#  Basic logger and env
# ---------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("improv_spotlight")

load_dotenv(".env.local")
load_dotenv(".env")

# path to your scenarios JSON file
SCENARIOS_PATH = os.path.join(os.path.dirname(__file__), "../data/access_data.json")


# ---------------------------------------------------------
#  Session state container
# ---------------------------------------------------------
class SessionState:
    """
    Holds state for a single improv session.
    """

    def __init__(self):
        self.player_name: Optional[str] = None
        self.current_round: int = 0
        self.max_rounds: int = 4
        self.rounds: List[Dict[str, Any]] = []  # each: {scenario_id, title, prompt, player_text, host_reaction}
        self.phase: str = "intro"  # intro | waiting_for_improv | reacting | finished
        self.current_scenario: Optional[Dict[str, Any]] = None
        self.used_ids: List[str] = []
        self.all_scenarios: List[Dict[str, Any]] = []
        self.improv_turns: int = 0


state = SessionState()


# ---------------------------------------------------------
#  Scenario utils
# ---------------------------------------------------------
def load_scenarios() -> List[Dict[str, Any]]:
    try:
        with open(SCENARIOS_PATH, "r", encoding="utf-8") as f:
            payload = json.load(f)
            return payload.get("scenarios", [])
    except FileNotFoundError:
        logger.error(f"Scenarios file not found at {SCENARIOS_PATH}")
        return []
    except Exception as e:
        logger.exception("Failed to load scenarios: %s", e)
        return []


def choose_unused_scenario() -> Optional[Dict[str, Any]]:
    available = [s for s in state.all_scenarios if s.get("id") not in state.used_ids]
    if not available:
        # reset used list if we've exhausted scenarios
        state.used_ids = []
        available = state.all_scenarios[:]
    if not available:
        return None
    choice = random.choice(available)
    state.used_ids.append(choice.get("id"))
    return choice


# ---------------------------------------------------------
#  Host system prompt (English; new personality)
# ---------------------------------------------------------
def host_system_prompt() -> str:
    """
    Clear English-only system prompt that tells the agent how to behave.
    """
    return """
You are the host of a lively improv show called "Improv Spotlight".
Identity:
- Role: the on-stage host and judge.
- Persona: energetic, theatrical, warm, and occasionally playfully critical.
- Language: English ONLY. Use simple, natural English (no slang that the player might not understand).
- Tone: enthusiastic and supportive most of the time; occasionally give short, constructive critique.
- Keep responses short (1-3 sentences) for prompts and reactions.
- Always be respectful. Never insult the player or use abusive language.

Show format:
1. INTRO: welcome the player, explain rules briefly, and ask for their name if not known.
2. ROUNDS: run `max_rounds` rounds (default 4).
   - For each round: announce the round, clearly present the scenario (who you are, what's happening, what's at stake).
   - Tell the player to "Start when ready" and instruct them they may say "End scene" to finish or pause for ~2.5 seconds.
   - Wait for the player's improvisation. Detect end via explicit phrase or pause.
   - When the player finishes, offer a short reaction: mention one thing that worked and one suggestion to try.
   - Randomize reaction tone per round with roughly this distribution: 50% positive, 30% neutral, 20% gentle critique.
3. OUTRO: when rounds complete, give a short closing summary that highlights 2-3 standout moments and a final tip.

Behavior rules:
- Save each round to session state with scenario, player text, and host reaction.
- If player says "stop game" or "end show" at any time, confirm and end the session gracefully.
- If the player's content includes disallowed material, redirect briefly and ask them to try a different direction.

Example reaction formats:
- Positive: "That was delightful — I loved your physical choices. Try lingering on the character's reaction next time."
- Neutral: "Solid choices and clear voice. You might push the stakes a little more for bigger laughs."
- Gentle critique: "Good idea, but it felt rushed — slow down and let the audience react."

Always use plain English and follow the structure above.
"""


# ---------------------------------------------------------
#  Host agent class
# ---------------------------------------------------------
class SpotlightHost(Agent):
    def __init__(self):
        logger.info(">>> Initializing SpotlightHost agent")
        state.all_scenarios = load_scenarios()
        super().__init__(instructions=host_system_prompt())

    # called when the agent is started and connected to a room
    async def on_enter(self) -> None:
        state.phase = "intro"
        
        # Try multiple ways to get player name
        player_name_found = False
        
        # Method 1: Check participant metadata (MOST RELIABLE)
        try:
            if hasattr(self.session, 'room') and self.session.room:
                # Get all participants
                participants = list(self.session.room.remote_participants.values())
                logger.info(f"Found {len(participants)} remote participants")
                
                for participant in participants:
                    logger.info(f"Participant: {participant.identity}, metadata: {participant.metadata}")
                    if participant.metadata:
                        import json
                        try:
                            participant_metadata = json.loads(participant.metadata)
                            if 'playerName' in participant_metadata:
                                state.player_name = participant_metadata['playerName']
                                player_name_found = True
                                logger.info(f"✓ Player name from participant metadata: {state.player_name}")
                                break
                        except:
                            pass
                    
                    # Also try participant identity/name as fallback
                    if not player_name_found and participant.identity and participant.identity != 'agent':
                        state.player_name = participant.identity
                        player_name_found = True
                        logger.info(f"✓ Player name from participant identity: {state.player_name}")
                        break
        except Exception as e:
            logger.warning(f"Could not get participant metadata: {e}")
        
        # Method 2: Check room metadata
        if not player_name_found:
            try:
                if hasattr(self.session, 'room') and self.session.room:
                    logger.info(f"Room metadata: {self.session.room.metadata}")
                    if self.session.room.metadata:
                        import json
                        room_metadata = json.loads(self.session.room.metadata)
                        if 'playerName' in room_metadata:
                            state.player_name = room_metadata['playerName']
                            player_name_found = True
                            logger.info(f"✓ Player name from room metadata: {state.player_name}")
            except Exception as e:
                logger.warning(f"Could not parse room metadata: {e}")
        
        # Generate welcome message
        if player_name_found and state.player_name:
            # Player name already known - greet them directly
            logger.info(f"Greeting player by name: {state.player_name}")
            await self.session.generate_reply(
                instructions=(
                    f"Give a bright, energetic welcome specifically to {state.player_name}. "
                    f"Say something like 'Welcome {state.player_name}! Great to have you here!' "
                    "Then explain: 'You'll get 4 short improv scenes. "
                    "I'll set each scene, you act it out, then say End scene or pause to finish. "
                    "I'll give a quick reaction after each.' "
                    "Keep it energetic and under 30 seconds. IMPORTANT: Use their name in the greeting."
                )
            )
        else:
            # Ask for player name
            logger.info("Player name not found, asking for it")
            await self.session.generate_reply(
                instructions=(
                    "Give a bright, short welcome. Explain: 'You'll get 4 short improv scenes. "
                    "I'll set each scene, you act it out, then say End scene or pause to finish. "
                    "I'll give a quick reaction after each. What's your name?' "
                    "Keep it energetic and under 30 seconds."
                )
            )

    @function_tool()
    async def set_player(self, ctx: RunContext, name: str) -> str:
        """
        Set the player's name in the session.
        """
        state.player_name = name.strip() if name else "Player"
        logger.info("Player set to: %s", state.player_name)
        return f"Great to meet you, {state.player_name}! Ready to play Improv Spotlight?"

    @function_tool()
    async def next_scene(self, ctx: RunContext) -> Dict[str, Any]:
        """
        Start the next round by selecting a scenario and returning it.
        """
        if state.current_round >= state.max_rounds:
            return {"error": "All rounds are complete."}

        scene = choose_unused_scenario()
        if not scene:
            return {"error": "No scenarios available."}

        state.current_scenario = scene
        state.phase = "waiting_for_improv"
        state.improv_turns = 0

        logger.info("Starting round %d: %s", state.current_round + 1, scene.get("title"))

        return {
            "round_number": state.current_round + 1,
            "max_rounds": state.max_rounds,
            "title": scene.get("title"),
            "prompt": scene.get("scenario"),
            "instruction": "Start when you're ready. Say 'End scene' or pause to finish."
        }

    @function_tool()
    async def complete_improv(self, ctx: RunContext, player_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Called when the player finishes a scene. Generate and store a host reaction,
        increment round counters, and indicate whether the game continues.
        """
        state.improv_turns += 1

        if not state.current_scenario:
            return {"error": "No active scenario to complete."}

        player_text = (player_text or "[performance delivered]").strip()

        # Reaction generation (simple randomized templates)
        positive_templates = [
            "That was wonderful — your choices felt honest and clear. Try stretching the pause before the punchline next time.",
            "Really enjoyable — you nailed the character. You could push the physicality a bit more to sell it.",
            "Great energy throughout! Consider letting the reaction breathe a little longer for bigger laughs."
        ]
        neutral_templates = [
            "Solid performance — the scene was easy to follow. You might experiment with raising the stakes.",
            "Good clarity and voice. Try adding one strong, specific detail to make it pop next round.",
            "Nice phrasing. A bolder choice in the middle could make the scene stand out more."
        ]
        critique_templates = [
            "Interesting idea, but it felt rushed. Slow down and let moments land to build impact.",
            "Good attempt, though the character was a bit flat. Pick one strong trait and commit.",
            "You had good instincts, but the stakes were low — choose a clearer objective to drive the scene."
        ]

        # Randomly pick tone with weighted distribution
        tone_roll = random.random()
        if tone_roll < 0.5:
            reaction = random.choice(positive_templates)
            tone = "positive"
        elif tone_roll < 0.8:
            reaction = random.choice(neutral_templates)
            tone = "neutral"
        else:
            reaction = random.choice(critique_templates)
            tone = "gentle_critique"

        # store round
        state.rounds.append({
            "round_index": state.current_round + 1,
            "scenario_id": state.current_scenario.get("id"),
            "scenario_title": state.current_scenario.get("title"),
            "scenario_prompt": state.current_scenario.get("scenario"),
            "player_text": player_text,
            "host_reaction": reaction,
            "reaction_tone": tone,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

        state.current_round += 1
        state.phase = "reacting"

        logger.info("Round %d completed. Reaction tone: %s", state.current_round, tone)

        if state.current_round >= state.max_rounds:
            # game finished
            summary = await self._compose_closing_summary()
            state.phase = "finished"
            return {
                "status": "finished",
                "reaction": reaction,
                "closing_summary": summary,
                "rounds": state.rounds
            }
        else:
            # prepare for next round
            return {
                "status": "continue",
                "reaction": reaction,
                "next_round_number": state.current_round + 1,
                "message": "Get ready for the next scene!"
            }

    @function_tool()
    async def finish_show(self, ctx: RunContext) -> Dict[str, Any]:
        """
        Forcefully end the show and return a final summary.
        """
        state.phase = "finished"
        summary = await self._compose_closing_summary()
        return {
            "status": "ended",
            "player_name": state.player_name,
            "rounds_completed": state.current_round,
            "summary": summary,
            "rounds": state.rounds
        }

    async def _compose_closing_summary(self) -> str:
        """
        Create a short closing summary based on stored rounds.
        """
        if not state.rounds:
            return f"Thanks for joining, {state.player_name or 'player'}! You showed great willingness to try — come back to practice and play again."

        # pick highlights - choose up to two standout snippets from player_texts
        highlights = []
        for r in state.rounds[:2]:
            snippet = r.get("player_text", "")
            # shorten snippet for summary
            snippet_short = (snippet[:60] + "...") if len(snippet) > 60 else snippet
            highlights.append(f"Round {r['round_index']}: \"{snippet_short}\"")

        # infer style heuristically from reactions
        positive_count = sum(1 for r in state.rounds if r.get("reaction_tone") == "positive")
        critique_count = sum(1 for r in state.rounds if r.get("reaction_tone") == "gentle_critique")

        if positive_count >= critique_count:
            style = "you lean toward bold, playful choices"
        else:
            style = "you might focus on clearer objectives and steady pacing"

        tip = "Try committing to one clear objective per scene to make your choices bolder."

        return (
            f"Final thoughts for {state.player_name or 'the player'}: {style}. "
            f"Highlights: {' | '.join(highlights)}. {tip}"
        )

    @function_tool()
    async def session_status(self, ctx: RunContext) -> Dict[str, Any]:
        """
        Return a short status summary of the current session.
        """
        return {
            "player_name": state.player_name,
            "current_round": state.current_round,
            "max_rounds": state.max_rounds,
            "phase": state.phase,
            "rounds_saved": len(state.rounds),
            "current_title": state.current_scenario.get("title") if state.current_scenario else None
        }


# ---------------------------------------------------------
#  Prewarm and entrypoint for job runner
# ---------------------------------------------------------
def prewarm(proc: JobProcess):
    """
    Preload VAD model or other heavy assets for faster startup.
    """
    try:
        proc.userdata["vad"] = silero.VAD.load()
        logger.info("Prewarmed silero VAD.")
    except Exception as e:
        logger.warning("Could not prewarm VAD: %s", e)


async def entrypoint(ctx: JobContext):
    logger.info(">> Booting Improv Spotlight agent")
    vad = ctx.proc.userdata.get("vad")
    if vad is None:
        # try lazy load
        try:
            vad = silero.VAD.load()
            logger.info("Loaded VAD lazily in entrypoint.")
        except Exception:
            vad = None

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-ken",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=vad,
        preemptive_generation=True,
    )

    await ctx.connect()

    await session.start(
        agent=SpotlightHost(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )


# ---------------------------------------------------------
#  Run as a script
# ---------------------------------------------------------
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))