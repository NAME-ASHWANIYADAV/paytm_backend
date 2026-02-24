"""AI Chat Service — Claude Haiku powered trip planning assistant."""
from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

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

NEVER give generic responses. Always be specific to the destination and query.
When user mentions a city/destination, immediately give useful info — don't ask them to repeat.
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

    # Build conversation history (keep full context)
    messages = []
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

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    reply = response.content[0].text
    trip_generated = any(
        kw in reply.lower()
        for kw in ["plan ready", "itinerary", "budget", "₹", "total cost", "per person", "transport", "stay"]
    )

    return reply, trip_generated


def _fallback_response(message: str) -> tuple[str, bool]:
    """Smart fallback when Claude API is not available."""
    msg_lower = message.lower()

    # Destination-specific responses
    destinations = {
        "rishikesh": {
            "reply": (
                "Rishikesh trip plan ready hai bhai! 🏞️\n\n"
                "📍 Rishikesh, Uttarakhand\n"
                "📅 Weekend trip (Fri-Sun) best hai\n\n"
                "🚂 Transport:\n"
                "• Train: Delhi → Haridwar ₹380 (Sleeper), ₹180 (2S with concession)\n"
                "• Local bus: Haridwar → Rishikesh ₹60 (1 hr)\n\n"
                "🏨 Stay Options:\n"
                "• Zostel Rishikesh: ₹500/night (dorm)\n"
                "• Backpacker Hostel: ₹400/night\n"
                "• Camping by Ganga: ₹800/night (tent + meals)\n\n"
                "🎯 Activities:\n"
                "• White Water Rafting (16km): ₹500-700\n"
                "• Bungee Jumping: ₹3,500\n"
                "• Laxman Jhula + Ram Jhula: FREE\n"
                "• Ganga Aarti (Triveni Ghat): FREE\n"
                "• Beatles Ashram: ₹150 (₹75 student)\n"
                "• Café hopping (Little Buddha Café): ₹200-300\n\n"
                "💰 Total: ~₹1,850-2,200/person for weekend\n"
                "💡 Pro tip: Book Shatabdi train for day trip, saves hostel cost!\n\n"
                "Paytm se book karo, cashback milega! 💙"
            ),
            "trip": True,
        },
        "goa": {
            "reply": (
                "Goa trip plan ready! 🏖️ Sun, sand aur savings!\n\n"
                "📍 North Goa (Anjuna, Vagator, Calangute)\n"
                "📅 3 Nights recommended (Thu-Sun best)\n\n"
                "🚂 Transport:\n"
                "• Train: Any city → Madgaon ₹800-1200 (Sleeper)\n"
                "• Flight: ₹2,500-4,000 (book 2 weeks early)\n"
                "• Madgaon → Beach: ₹200 (local bus/shared auto)\n\n"
                "🏨 Stay:\n"
                "• Zostel Goa: ₹600/night (dorm, pool hai!)\n"
                "• Old Quarter Hostel: ₹500/night\n"
                "• Airbnb villa (5 log share): ₹800/person/night\n\n"
                "🎯 Must Do:\n"
                "• Scooty rent: ₹350/day (Activa)\n"
                "• Dudhsagar Falls trip: ₹800\n"
                "• Fort Aguada + Chapora Fort: FREE\n"
                "• Saturday Night Market (Arpora): FREE entry\n"
                "• Thalassa/Artjuna café: ₹400-600\n\n"
                "💰 Total: ~₹3,500-4,500/person for 3 nights\n"
                "💡 Pro tip: Go in groups of 5+, villa split bohot sasta padta hai!\n\n"
                "Paytm se book karo, cashback milega! 💙"
            ),
            "trip": True,
        },
        "manali": {
            "reply": (
                "Manali plan ready bhai! ❄️🏔️ Snow + Adventures!\n\n"
                "📍 Old Manali + Solang Valley\n"
                "📅 4 Nights best (book Tue-Sat for cheap buses)\n\n"
                "🚌 Transport:\n"
                "• Volvo Bus Delhi→Manali: ₹1,200-1,500 (HRTC best)\n"
                "• Semi-Deluxe Bus: ₹800\n"
                "• Local taxi Manali→Solang: ₹500 (shared)\n\n"
                "🏨 Stay:\n"
                "• Hosteller Old Manali: ₹450/night\n"
                "• Guest house Old Manali: ₹300-500/night\n"
                "• Camps in Sethan: ₹1,000/night (meals included)\n\n"
                "🎯 Activities:\n"
                "• Solang Valley (paragliding): ₹1,500\n"
                "• Rohtang Pass trip: ₹800 (shared)\n"
                "• Hadimba Temple: FREE\n"
                "• Mall Road walk + cafés: ₹200-300\n"
                "• Jogini Waterfall trek: FREE\n\n"
                "💰 Total: ~₹2,800-3,500/person\n"
                "💡 Pro tip: December-Feb mein snow guaranteed! Off-season mein sasta!\n\n"
                "Paytm se book karo, cashback milega! 💙"
            ),
            "trip": True,
        },
        "udaipur": {
            "reply": (
                "Udaipur trip plan ready! 🏰 City of Lakes!\n\n"
                "📍 Udaipur, Rajasthan\n"
                "📅 2-3 Nights perfect hai\n\n"
                "🚂 Transport:\n"
                "• Train Delhi→Udaipur: ₹500 (Sleeper), ₹250 (2S student)\n"
                "• Bus: ₹600-900 (Volvo)\n\n"
                "🏨 Stay:\n"
                "• Zostel Udaipur: ₹500/night (lake view!)\n"
                "• Backpacker Panda: ₹400/night\n"
                "• Budget hotel Lal Ghat: ₹600-800/night\n\n"
                "🎯 Must Visit:\n"
                "• City Palace: ₹300 (₹150 student)\n"
                "• Lake Pichola boat ride: ₹400\n"
                "• Jagdish Temple: FREE\n"
                "• Sajjangarh Monsoon Palace: ₹80\n"
                "• Fateh Sagar Lake: FREE\n"
                "• Ambrai Ghat sunset: FREE (best view!)\n\n"
                "🍛 Food: ₹200-300/day (dal baati, gatte ki sabzi)\n\n"
                "💰 Total: ~₹2,000-2,800/person for 3 nights\n"
                "💡 Pro tip: 4 bande ho toh auto share karo, ₹50/person anywhere!\n\n"
                "Paytm se book karo, cashback milega! 💙"
            ),
            "trip": True,
        },
        "jaipur": {
            "reply": (
                "Pink City ka plan ready! 🏰 Royal Rajasthan!\n\n"
                "📍 Jaipur, Rajasthan\n"
                "📅 2 Nights perfect hai\n\n"
                "🚂 Transport:\n"
                "• Train Delhi→Jaipur: ₹270 (Sleeper), ₹135 (2S student concession)\n"
                "• Bus: ₹500-800 (RSRTC Volvo)\n\n"
                "🏨 Stay:\n"
                "• Moustache Hostel: ₹400/night (rooftop party!)\n"
                "• Zostel Jaipur: ₹500/night\n"
                "• Heritage haveli: ₹700-1000/night\n\n"
                "🎯 Must Do:\n"
                "• Amber Fort: ₹200 (₹100 student)\n"
                "• Hawa Mahal: ₹50 (₹25 student)\n"
                "• Nahargarh Fort sunset: ₹200\n"
                "• City Palace: ₹300\n"
                "• Jal Mahal (selfie only): FREE\n"
                "• Johri Bazaar shopping: Budget dependent\n\n"
                "🍛 Food: ₹200-300/day (LMB thali ₹350 must try!)\n\n"
                "💰 Total: ~₹2,200-2,800/person\n"
                "💡 Pro tip: Composite ticket ₹500 mein 7 monuments cover hote hain!\n\n"
                "Paytm se book karo, cashback milega! 💙"
            ),
            "trip": True,
        },
        "varanasi": {
            "reply": (
                "Kashi ja raha hai bhai! 🙏 Spiritual + cultural trip!\n\n"
                "📍 Varanasi, Uttar Pradesh\n"
                "📅 2 Nights perfect hai\n\n"
                "🚂 Transport:\n"
                "• Train: ₹300-500 (Sleeper from most cities)\n"
                "• Student concession: 50% off on 2S!\n\n"
                "🏨 Stay:\n"
                "• Zostel Varanasi: ₹400/night (ghat view!)\n"
                "• Backpacker hostel: ₹300/night\n"
                "• Guest house Assi Ghat: ₹500/night\n\n"
                "🎯 Must Do:\n"
                "• Ganga Aarti (Dashashwamedh Ghat): FREE 🔥\n"
                "• Boat ride sunrise: ₹150 (shared)\n"
                "• Kashi Vishwanath Temple: FREE\n"
                "• BHU campus walk: FREE\n"
                "• Lassi at Blue Lassi Shop: ₹60\n"
                "• Sarnath day trip: ₹100 auto, ₹25 entry\n\n"
                "🍛 Food: ₹150-250/day (kachori, chaat, banarasi paan ₹30)\n\n"
                "💰 Total: ~₹1,500-2,000/person\n"
                "💡 Pro tip: Subah 5 baje ka boat ride sunrise best experience hai!\n\n"
                "Paytm se book karo, cashback milega! 💙"
            ),
            "trip": True,
        },
    }

    for dest, data in destinations.items():
        if dest in msg_lower:
            return data["reply"], data["trip"]

    # Trip/travel related
    if any(kw in msg_lower for kw in ["trip", "plan", "travel", "ghum", "jana", "jao", "chalte", "chalo", "weekend"]):
        return (
            "Badhiya! 🗺️ Kaha plan kar rahe ho?\n\n"
            "Budget-friendly student destinations:\n"
            "🏞 Rishikesh — ₹1,850/person (adventure!)\n"
            "🏰 Jaipur — ₹2,200/person (heritage)\n"
            "🕌 Varanasi — ₹1,500/person (spiritual)\n"
            "🏰 Udaipur — ₹2,500/person (lakes!)\n"
            "❄️ Manali — ₹2,800/person (mountains)\n"
            "🏖 Goa — ₹3,500/person (beaches)\n\n"
            "Destination bol, kitne log hain, aur budget — full plan bana deta hu! 🚀"
        ), False

    # Default
    return (
        "Hey! 👋 Main CampusGPT hu — tera AI trip planner!\n\n"
        "Mujhe bata:\n"
        "• 📍 Kaha jana hai?\n"
        "• 👥 Kitne log hain?\n"
        "• 💰 Budget kitna hai per person?\n"
        "• 📅 Kab jana hai?\n\n"
        "Main full detailed plan dunga — transport, stay, activities, food sab ka breakdown! 🗺️✨"
    ), False
