"""AI Chat Service — Claude Haiku powered trip planning assistant."""
from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """You are CampusGPT, a friendly AI travel planner built into Paytm Campus OS. 
You help Indian college students plan trips on a budget.

Rules:
- Always respond in casual Hinglish (Hindi + English mix)
- Keep responses SHORT (max 150 words)
- Always include emojis
- Always mention specific prices in ₹ (Indian Rupees)
- Suggest budget stays (hostels, dharamshalas), cheap transport (trains/buses), and free activities
- If asked about a destination, give a quick itinerary with transport + stay + activities + total budget
- Mention student discounts wherever applicable
- Sign off suggestions with "Paytm se book karo, cashback milega! 💙"
- If the user asks something unrelated to travel, gently redirect to trip planning

Example response format:
"Done bhai! 🎉 [Destination] trip ka plan ready hai.
📍 [Place]
📅 [Dates suggestion]
👥 [Group size] | 💰 ₹[price]/person

[Brief breakdown]
Paytm se book karo, cashback milega! 💙"
"""


async def get_ai_response(message: str, history: list[dict]) -> tuple[str, bool]:
    """
    Get AI response for trip planning chat.
    Returns (reply_text, trip_generated_flag).
    Falls back to template response if no API key.
    """
    if ANTHROPIC_API_KEY:
        try:
            return await _claude_response(message, history)
        except Exception as e:
            print(f"Claude API error: {e}")
            return _fallback_response(message)
    else:
        return _fallback_response(message)


async def _claude_response(message: str, history: list[dict]) -> tuple[str, bool]:
    """Call Anthropic Claude Haiku API for response."""
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Build conversation history
    messages = []
    for msg in history:
        role = "user" if msg.get("role") == "user" else "assistant"
        messages.append({"role": role, "content": msg.get("text", "")})

    # Add current user message
    messages.append({"role": "user", "content": message})

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    reply = response.content[0].text
    trip_generated = any(
        kw in reply.lower()
        for kw in ["plan ready", "itinerary", "budget", "₹", "book"]
    )

    return reply, trip_generated


def _fallback_response(message: str) -> tuple[str, bool]:
    """Smart fallback when Claude API is not available."""
    msg_lower = message.lower()

    # Destination-specific responses
    destinations = {
        "rishikesh": {
            "reply": (
                "Done bhai! 🎉 Rishikesh trip ka full plan ready hai.\n\n"
                "📍 Rishikesh, Uttarakhand\n"
                "📅 Weekend trip (Fri-Sun)\n"
                "👥 Group of 5 | 💰 ₹1,850/person\n\n"
                "🚂 Train: ₹380 (Sleeper) + 🚌 Local: ₹60\n"
                "🏨 Backpacker Hostel: ₹400/night\n"
                "🏄 Rafting: ₹500 | Café hopping: ₹200\n"
                "🙏 Ganga Aarti + Laxman Jhula: FREE\n\n"
                "Total: ₹1,850/person (within budget ✅)\n"
                "Paytm se book karo, cashback milega! 💙"
            ),
            "trip": True,
        },
        "goa": {
            "reply": (
                "Goa ja raha hai bhai? 🏖️ Sahi hai!\n\n"
                "📍 North Goa (Anjuna/Vagator)\n"
                "📅 3 Nights best hai\n"
                "👥 4 log | 💰 ₹3,500/person\n\n"
                "🚂 Train: ₹800 (Sleeper) Madgaon tak\n"
                "🏨 Beach Hostel: ₹500/night\n"
                "🏍 Scooty rent: ₹350/day\n"
                "🍕 Food budget: ₹500/day\n"
                "🏊 Beach + Fort + Market: FREE\n\n"
                "Total: ₹3,500/person approx\n"
                "Paytm se book karo, cashback milega! 💙"
            ),
            "trip": True,
        },
        "manali": {
            "reply": (
                "Manali trip plan kar diya bhai! ❄️🏔️\n\n"
                "📍 Manali, Himachal Pradesh\n"
                "📅 4 Nights recommended\n"
                "👥 5 log | 💰 ₹2,800/person\n\n"
                "🚌 Volvo Bus: ₹1,200 (Delhi se)\n"
                "🏨 Hostel Old Manali: ₹400/night\n"
                "🏔 Solang Valley + Rohtang: ₹800\n"
                "☕ Mall Road + Cafés: ₹300\n\n"
                "Total: ₹2,800/person\n"
                "Paytm se book karo, cashback milega! 💙"
            ),
            "trip": True,
        },
        "jaipur": {
            "reply": (
                "Pink City jaa raha hai! 🏰 Badhiya choice!\n\n"
                "📍 Jaipur, Rajasthan\n"
                "📅 2 Nights perfect hai\n"
                "👥 4 log | 💰 ₹2,200/person\n\n"
                "🚂 Train: ₹450 (Sleeper)\n"
                "🏨 Heritage Hostel: ₹350/night\n"
                "🏰 Amber Fort + Hawa Mahal: ₹200\n"
                "🍛 Dal Baati + Lassi: ₹300/day\n\n"
                "Total: ₹2,200/person\n"
                "Paytm se book karo, cashback milega! 💙"
            ),
            "trip": True,
        },
    }

    for dest, data in destinations.items():
        if dest in msg_lower:
            return data["reply"], data["trip"]

    # Generic trip-related
    if any(kw in msg_lower for kw in ["trip", "plan", "travel", "ghum", "jana"]):
        return (
            "Bata bhai kaha jana hai? 🗺️\n\n"
            "Popular student destinations:\n"
            "🏔 Manali — ₹2,800/person\n"
            "🏖 Goa — ₹3,500/person\n"
            "🏞 Rishikesh — ₹1,850/person\n"
            "🏰 Jaipur — ₹2,200/person\n"
            "🕌 Varanasi — ₹1,500/person\n\n"
            "Destination bol, plan bana deta hu! 🚀"
        ), False

    # Default
    return (
        "Hey! 👋 Main CampusGPT hu — tera personal trip planner!\n\n"
        "Mujhe bol:\n"
        "• Kaha jana hai? (Rishikesh, Goa, Manali...)\n"
        "• Kitne log? Budget kitna?\n"
        "• Weekend trip ya long trip?\n\n"
        "Main sab plan kar dunga — transport, stay, activities sab! 🗺️✨"
    ), False
