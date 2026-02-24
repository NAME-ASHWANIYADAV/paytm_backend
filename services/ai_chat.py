"""AI Chat Service — Groq (Llama 3.3 70B) powered trip planning assistant."""
from __future__ import annotations

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# Keep Anthropic as optional fallback
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """You are CampusGPT, an AI travel planner built into Paytm Campus OS for Indian college students.

IMPORTANT RULES:
- ALWAYS respond in Hinglish (Hindi + English mix naturally)
- Give DETAILED, SPECIFIC answers — include real prices, real places, real timings
- REMEMBER the full conversation context — refer to previous messages when answering follow-ups
- When someone asks about a trip, give a COMPLETE plan with:
  • Transport options with exact prices (trains, buses, flights)
  • Stay options with prices (hostels, hotels, dharamshalas)
  • Activities and must-visit places with entry fees
  • Food budget per day
  • Total cost breakdown per person
  • Pro tips for students (discounts, best times to visit, etc.)
- Use emojis naturally but don't overdo it
- Mention student discounts, concession tickets, group booking savings
- For follow-up questions, build on what was discussed before
- If user asks about booking, mention Paytm features
- Give day-wise itinerary when asked for detailed plans
- Include local transport tips (auto fares, bus routes, metro info)
- Suggest budget, mid-range, and premium options when relevant
- Be conversational and helpful like a friend who has traveled a lot
- End trip plans with "Paytm se book karo, cashback milega! 💙"

NEVER give generic responses. Always be specific to the destination and query.
When user mentions a city/destination, immediately give useful info — don't ask them to repeat.
If user gives a from-to route, plan the COMPLETE journey including how to get there, where to stay, and what to do.
"""

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


async def get_ai_response(message: str, history: list[dict]) -> tuple[str, bool]:
    """
    Get AI response for trip planning chat.
    Priority: Groq (free) -> Anthropic (paid) -> Fallback.
    Returns (reply_text, trip_generated_flag).
    """
    # Try Groq first (free tier)
    if GROQ_API_KEY:
        try:
            return await _groq_response(message, history)
        except Exception as e:
            print(f"[CampusGPT] Groq API error: {e}")

    # Try Anthropic as fallback
    if ANTHROPIC_API_KEY:
        try:
            return await _claude_response(message, history)
        except Exception as e:
            print(f"[CampusGPT] Claude API error: {e}")

    # Final fallback
    return _fallback_response(message)


async def _groq_response(message: str, history: list[dict]) -> tuple[str, bool]:
    """Call Groq API (OpenAI-compatible) for response using Llama 3.3 70B."""

    # Build conversation messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in history:
        role = "user" if msg.get("role") == "user" else "assistant"
        text = msg.get("text", "")
        if text.strip():
            # Avoid consecutive same-role messages
            if messages and messages[-1]["role"] == role:
                messages[-1]["content"] += "\n" + text
            else:
                messages.append({"role": role, "content": text})

    # Add current user message
    if messages and messages[-1]["role"] == "user":
        messages[-1]["content"] += "\n" + message
    else:
        messages.append({"role": "user", "content": message})

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 0.7,
            },
        )
        response.raise_for_status()
        data = response.json()

    reply = data["choices"][0]["message"]["content"]
    trip_generated = any(
        kw in reply.lower()
        for kw in ["plan ready", "itinerary", "budget", "₹", "total cost",
                    "per person", "transport", "stay", "hotel", "hostel", "train"]
    )

    return reply, trip_generated


async def _claude_response(message: str, history: list[dict]) -> tuple[str, bool]:
    """Call Anthropic Claude Haiku API for response (paid fallback)."""
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    messages = []
    for msg in history:
        role = "user" if msg.get("role") == "user" else "assistant"
        text = msg.get("text", "")
        if text.strip():
            if messages and messages[-1]["role"] == role:
                messages[-1]["content"] += "\n" + text
            else:
                messages.append({"role": role, "content": text})

    if messages and messages[-1]["role"] == "user":
        messages[-1]["content"] += "\n" + message
    else:
        messages.append({"role": "user", "content": message})

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    reply = response.content[0].text
    trip_generated = any(
        kw in reply.lower()
        for kw in ["plan ready", "itinerary", "budget", "₹", "total cost",
                    "per person", "transport", "stay"]
    )

    return reply, trip_generated


def _fallback_response(message: str) -> tuple[str, bool]:
    """Fallback when no AI API is available."""
    msg_lower = message.lower()

    destinations = {
        "rishikesh": (
            "Rishikesh trip plan ready! 🏞️\n\n"
            "📍 Rishikesh, Uttarakhand\n📅 Weekend trip best\n\n"
            "🚂 Train: Delhi→Haridwar ₹380 (Sleeper)\n"
            "🏨 Zostel: ₹500/night | Hostel: ₹400/night\n"
            "🎯 Rafting: ₹500 | Beatles Ashram: ₹75 (student)\n"
            "💰 Total: ~₹1,850-2,200/person\n\n"
            "Paytm se book karo, cashback milega! 💙"
        ),
        "goa": (
            "Goa plan ready! 🏖️\n\n📍 North Goa\n📅 3 Nights\n\n"
            "🚂 Train→Madgaon: ₹800 | ✈️ Flight: ₹2,500+\n"
            "🏨 Zostel: ₹600/night | Villa (5 share): ₹800/person\n"
            "🏍 Scooty: ₹350/day | Dudhsagar: ₹800\n"
            "💰 Total: ~₹3,500-4,500/person\n\n"
            "Paytm se book karo, cashback milega! 💙"
        ),
        "manali": (
            "Manali plan ready! ❄️\n\n📍 Old Manali\n📅 4 Nights\n\n"
            "🚌 Volvo Delhi→Manali: ₹1,200\n"
            "🏨 Hostel: ₹450/night | Camp: ₹1,000 (meals incl)\n"
            "🏔 Paragliding: ₹1,500 | Rohtang: ₹800\n"
            "💰 Total: ~₹2,800-3,500/person\n\n"
            "Paytm se book karo, cashback milega! 💙"
        ),
        "udaipur": (
            "Udaipur plan ready! 🏰\n\n📍 City of Lakes\n📅 2-3 Nights\n\n"
            "🚂 Train: ₹500 (Sleeper), ₹250 (student 2S)\n"
            "🏨 Zostel: ₹500/night (lake view!)\n"
            "🎯 City Palace: ₹150 (student) | Boat: ₹400\n"
            "💰 Total: ~₹2,000-2,800/person\n\n"
            "Paytm se book karo, cashback milega! 💙"
        ),
        "jaipur": (
            "Jaipur plan ready! 🏛️\n\n📍 Pink City\n📅 2 Nights\n\n"
            "🚂 Train Delhi→Jaipur: ₹270 (Sleeper)\n"
            "🏨 Moustache Hostel: ₹400/night\n"
            "🎯 Amber Fort: ₹100 (student) | Composite ticket: ₹500\n"
            "💰 Total: ~₹2,200-2,800/person\n\n"
            "Paytm se book karo, cashback milega! 💙"
        ),
        "varanasi": (
            "Varanasi plan ready! 🙏\n\n📍 Kashi\n📅 2 Nights\n\n"
            "🚂 Train: ₹300-500 (Sleeper, student 50% off!)\n"
            "🏨 Zostel: ₹400/night (ghat view!)\n"
            "🎯 Ganga Aarti: FREE | Boat ride: ₹150\n"
            "💰 Total: ~₹1,500-2,000/person\n\n"
            "Paytm se book karo, cashback milega! 💙"
        ),
    }

    for dest, reply in destinations.items():
        if dest in msg_lower:
            return reply, True

    if any(kw in msg_lower for kw in ["trip", "plan", "travel", "ghum", "jana", "jao", "weekend"]):
        return (
            "Badhiya! 🗺️ Popular student destinations:\n\n"
            "🏞 Rishikesh — ₹1,850/person\n🏰 Jaipur — ₹2,200/person\n"
            "🕌 Varanasi — ₹1,500/person\n🏰 Udaipur — ₹2,500/person\n"
            "❄️ Manali — ₹2,800/person\n🏖 Goa — ₹3,500/person\n\n"
            "Destination bol, full plan bana deta hu! 🚀"
        ), False

    return (
        "Hey! 👋 Main CampusGPT hu!\n\n"
        "Mujhe bata:\n• 📍 Kaha jana hai?\n• 👥 Kitne log?\n"
        "• 💰 Budget kitna?\n• 📅 Kab jana hai?\n\n"
        "Full detailed plan dunga! 🗺️✨"
    ), False
