# src/agent.py
import logging
from typing import Optional, Dict, List
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext,
)
from livekit.plugins import murf, deepgram, google, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.agents import MetricsCollectedEvent

from merchant import list_products, create_order, last_order, remove_item_from_order

load_dotenv(".env.local")

logger = logging.getLogger("agent")
logger.setLevel(logging.INFO)


class ShoppingAssistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
You are a voice shopping assistant. Use tools to list, add/remove, and checkout.
When user asks to browse, call list_products_tool with an optional filters dict.
When user confirms purchase, call add_to_cart_tool then checkout_tool.
Always use prices from the merchant layer (INR).
Keep replies concise.
"""
        )
        self.cart: List[Dict] = []

    # TOOL: list products (single optional filters dict)
    @function_tool
    async def list_products_tool(self, ctx: RunContext, filters: Optional[Dict] = None):
        filters = filters or {}
        prods = list_products(filters)
        if not prods:
            return {"products": [], "message": "No products found."}
        # send top-5 summarized products
        out = []
        for p in prods[:5]:
            out.append({"id": p["id"], "name": p["name"], "price": p["price"], "currency": p.get("currency", "INR"), "color": p.get("color")})
        return {"products": out}

    # TOOL: add to in-session cart
    @function_tool
    async def add_to_cart_tool(self, ctx: RunContext, product_id: str, quantity: Optional[int] = 1):
        p = next((x for x in list_products({}) if x["id"] == product_id), None)
        if not p:
            return {"ok": False, "message": "Product not found."}
        self.cart.append({"product_id": p["id"], "name": p["name"], "quantity": int(quantity or 1), "unit_price": p["price"]})
        total = sum(i["quantity"] * i["unit_price"] for i in self.cart)
        return {"ok": True, "cart": self.cart, "total": total, "currency": p.get("currency", "INR")}

    # TOOL: remove from in-session cart
    @function_tool
    async def remove_from_cart_tool(self, ctx: RunContext, product_id: str):
        before = len(self.cart)
        self.cart = [i for i in self.cart if i["product_id"] != product_id]
        after = len(self.cart)
        if before == after:
            return {"ok": False, "message": "Product not in cart."}
        total = sum(i["quantity"] * i["unit_price"] for i in self.cart)
        return {"ok": True, "cart": self.cart, "total": total}

    # TOOL: checkout -> calls merchant.create_order
    @function_tool
    async def checkout_tool(self, ctx: RunContext):
        if not self.cart:
            return {"ok": False, "message": "Cart empty."}
        line_items = [{"product_id": i["product_id"], "quantity": i["quantity"]} for i in self.cart]
        order = create_order(line_items)
        self.cart = []
        return {"ok": True, "order": order}

    # TOOL: view last (merchant)
    @function_tool
    async def view_last_order_tool(self, ctx: RunContext):
        order = last_order()
        if not order:
            return {"ok": False, "message": "No previous orders."}
        return {"ok": True, "order": order}

    # TOOL: remove item from merchant order
    @function_tool
    async def remove_item_tool(self, ctx: RunContext, order_id: str, product_id: str):
        updated = remove_item_from_order(order_id, product_id)
        if not updated:
            return {"ok": False, "message": "Order or product not found."}
        return {"ok": True, "order": updated}


def prewarm(proc: JobProcess):
    # No heavy prewarm needed here; placeholder
    return


async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

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
        vad=None,
        preemptive_generation=True,
    )

    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        logger.info(f"Usage: {usage_collector.get_summary()}")

    ctx.add_shutdown_callback(log_usage)

    # Start session — LLM will call the @function_tool functions as needed
    await session.start(agent=ShoppingAssistant(), room=ctx.room, room_input_options=RoomInputOptions(
        noise_cancellation=noise_cancellation.BVC()
    ))

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
