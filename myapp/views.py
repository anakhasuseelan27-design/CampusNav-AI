from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Location
from .algorithms import (
    get_turn_by_turn,
    normalize_location,
    location_details
)
import json


def home(request):
    return render(request, "myapp/home.html")


def clean_text(text):
    text = text.lower()
    text = text.replace("?", "")
    text = text.replace(".", "")
    text = text.replace(",", "")
    text = text.replace("&", " and ")
    text = text.replace("wnt", "want")
    text = text.replace("centre", "center")
    text = text.replace("need to go to", "go to")
    text = text.replace("need go to", "go to")
    return text.strip()


def find_locations_in_text(text):
    text = clean_text(text)
    found = []

    for location in location_details.keys():
        location_text = location.lower().replace("centre", "center")

        if location_text in text:
            found.append(location)

    found.sort(
        key=lambda loc: text.find(
            loc.lower().replace("centre", "center")
        )
    )

    return found


def extract_route_locations(text):
    text = clean_text(text)

    found_locations = find_locations_in_text(text)

    if len(found_locations) >= 2:
        return found_locations[0], found_locations[1]

    start = "Main Entrance"
    destination = ""

    text = text.replace("i am standing infront of", "from")
    text = text.replace("i am standing in front of", "from")
    text = text.replace("i am standing near", "from")
    text = text.replace("i am standing at", "from")
    text = text.replace("i am standing in", "from")

    text = text.replace("i am infront of", "from")
    text = text.replace("i am in front of", "from")
    text = text.replace("i am near", "from")
    text = text.replace("i am at", "from")
    text = text.replace("i am in", "from")

    text = text.replace("i want to go to", "to")
    text = text.replace("want to go to", "to")
    text = text.replace("want go to", "to")
    text = text.replace("take me to", "to")
    text = text.replace("go to", "to")

    if "from" in text and "to" in text:
        part = text.split("from", 1)[1]
        start, destination = part.split("to", 1)

    elif "to" in text:
        destination = text.split("to", 1)[1]

    start = normalize_location(start.strip())
    destination = normalize_location(destination.strip())

    return start, destination


@csrf_exempt
def chatbot(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    try:
        data = json.loads(request.body)
        prompt = data.get("message", "").strip()

        if not prompt:
            return JsonResponse({
                "reply": "Please enter a location or direction request."
            })

        text = prompt.lower()

        direction_words = [
            "to", "from", "direction", "directions",
            "route", "path", "go", "take me",
            "i am", "want", "standing", "near", "need"
        ]

        if any(word in text for word in direction_words):
            start, destination = extract_route_locations(text)

            if not destination:
                return JsonResponse({
                    "reply": "Please mention destination. Example: I am standing near Main Entrance and I want to go to Chemistry Lab"
                })

            path, instructions, distance, estimated_time = get_turn_by_turn(
                start,
                destination
            )

            if path:
                route = " → ".join(path)

                steps = ""
                for item in instructions:
                    steps += f"\n📍 Step {item['step']}: {item['instruction']}"

                reply = (
                    f"🗺️ Shortest Route:\n{route}\n\n"
                    f"📏 Total Distance: {distance} meters\n"
                    f"⏱️ Estimated Time: {estimated_time} seconds\n"
                    f"{steps}"
                )

                return JsonResponse({
                    "reply": reply,
                    "path": path,
                    "instructions": instructions,
                    "distance": distance,
                    "estimated_time": estimated_time
                })

            return JsonResponse({
                "reply": f"No route found between {start} and {destination}."
            })

        locations = Location.objects.all()

        for location in locations:
            if location.name.lower() in text:
                reply = (
                    f"{location.name} is located in "
                    f"{location.building}, "
                    f"{location.floor}. "
                    f"{location.description}"
                )
                return JsonResponse({"reply": reply})

        possible_location = normalize_location(prompt)

        if possible_location in location_details:
            return JsonResponse({
                "reply": (
                    f"{possible_location} is available in TOC H Einstein Block. "
                    f"Ask: I am standing near Main Entrance and I want to go to {possible_location}"
                )
            })

        return JsonResponse({
            "reply": "Sorry, I couldn't find that location. Try: I am standing near Main Entrance and I want to go to Chemistry Lab"
        })

    except Exception as e:
        return JsonResponse({"reply": f"Error: {str(e)}"})


def get_directions(request):
    start = request.GET.get("start", "Main Entrance")
    end = request.GET.get("end", "")

    start = normalize_location(start)
    end = normalize_location(end)

    path, instructions, distance, estimated_time = get_turn_by_turn(start, end)

    return JsonResponse({
        "path": path,
        "instructions": instructions,
        "distance": distance,
        "estimated_time": estimated_time,
        "route": " → ".join(path) if path else ""
    })