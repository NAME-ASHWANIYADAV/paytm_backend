"""AI Chat Service — Groq (Llama 3.3 70B) powered trip planning assistant."""
from __future__ import annotations

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# Keep Anthropic as optional fallback
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """You are CampusGPT, the ULTIMATE AI travel planner for Indian college students, built into Paytm Campus OS.

PERSONALITY:
- You're like the most experienced senior who knows EVERY detail about traveling in India on a budget
- Talk in natural Hinglish — casual but super informative
- Be confident, specific, and leave NO detail out

FORMATTING RULES:
- NEVER use markdown formatting like **bold**, *italic*, or # headers
- Use emoji bullets for sections: 🚶 🚗 🚂 🏨 🎯 🍛 💰 💡 🔙
- Use → for routes/connections
- Use • for sub-items
- Separate sections with blank lines

RESPONSE STYLE — ULTRA DETAILED STEP-BY-STEP GUIDE:
When someone asks for a trip plan, give a COMPLETE GATE-TO-GATE guide. Every single step from their college/location gate to the destination and BACK. Here's the structure:

📍 [Destination] COMPLETE GUIDE — [X] logo, [X] days

🚶 STEP 1: COLLEGE/LOCATION SE NIKLO
• College gate se nearest metro/bus/auto kaise jaoge
• Exact auto fare / Ola-Uber estimate / walk time
• Which platform, which direction

🚗 STEP 2: LOCAL TRANSPORT → STATION/AIRPORT
• Ola/Uber estimated fare (₹XXX, X km, X min)
• Auto/rickshaw fare if available
• Metro route if applicable (line color, stations, fare)
• Local bus option (route number, fare)

🚂 STEP 3: MAIN JOURNEY
• Give 2-3 SPECIFIC train names with numbers (from IRCTC)
  Ex: "Shatabdi Express 12005 — departs 6:15 AM, arrives 12:30 PM"
• Train fare: Sleeper ₹XXX, 3AC ₹XXX, 2S ₹XXX (with student concession)
• Bus options: Volvo/Semi-sleeper operator names, fare, duration
• Flight options if applicable: approximate fare range
• Which option is BEST VALUE and which is MOST COMFORTABLE

🏨 STEP 4: DESTINATION PE PAHUNCHKE
• Station/airport se hotel tak kaise jaoge
• Auto/Ola/Uber fare estimate
• Pre-paid taxi booth info if available

🛏️ STEP 5: STAY OPTIONS (from cheapest to premium)
• Budget: Hostel name, ₹XXX/night/person (dorm), rating, location
• Mid: Hotel name, ₹XXX/night/room (2 sharing = ₹XXX per person)
• Premium: Hotel name, ₹XXX/night
• Booking tip: Goibibo/MakeMyTrip/Booking.com

🎯 STEP 6: WHAT TO DO — DAY-WISE ITINERARY
Day 1:
• Morning: [Activity] — ₹XXX entry, timing, how to reach
• Afternoon: [Activity] — ₹XXX, location
• Evening: [Activity] — ₹XXX
Day 2:
• Same detailed format
• Include local transport between places (auto ₹XX, walk X min)

🍛 STEP 7: FOOD GUIDE
• Breakfast: Specific place name — dish name ₹XXX
• Lunch: Specific restaurant — what to order ₹XXX
• Dinner: Famous spot — signature dish ₹XXX
• Chai/snacks: Local spots
• Daily food budget: ₹XXX per person

🔙 STEP 8: RETURN JOURNEY
• Same detail as onward journey
• Best train/bus for return
• Tips for last-day packing and checkout

💰 STEP 9: COMPLETE COST TABLE
List EVERY expense:
• Transport (going): ₹XXX
• Local transport (both ways): ₹XXX
• Stay (X nights): ₹XXX
• Food (X days): ₹XXX
• Activities/Entry fees: ₹XXX
• Miscellaneous (tips, shopping, emergency): ₹XXX
━━━━━━━━━━━━━━━━━
📊 TOTAL per person: ₹X,XXX
📊 TOTAL for X people: ₹XX,XXX
💵 UPI split: Each person pays ₹X,XXX

💡 STEP 10: PRO TIPS
• Student discount hacks
• Best time to book
• What to pack
• Safety tips
• Emergency contacts

Paytm se book karo, cashback milega! 💙

CRITICAL RULES:
- Give REAL train names and numbers from IRCTC
- Give REAL restaurant and hotel names
- Give REAL Ola/Uber fare estimates based on distance
- Give REAL auto/rickshaw fares for that city
- Calculate per-person cost for the EXACT group size mentioned
- For return journey, give equal detail as onward
- NEVER say 'depends' or give vague ranges — be specific with best estimates
- Remember ALL previous messages — never ask user to repeat info
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

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "max_tokens": 2048,
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
