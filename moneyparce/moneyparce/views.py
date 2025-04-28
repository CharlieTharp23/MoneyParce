import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from django.http import JsonResponse
import google.generativeai as genai


oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)


def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    return redirect(request.build_absolute_uri(reverse("index")))

def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )

def index(request):
    return render(
        request,
        "index.html",
        context={
            "session": request.session.get("user"),
            "pretty": json.dumps(request.session.get("user"), indent=4),
        },
    )

def chatbot(request):
    if request.method == 'POST':
        user_input = request.POST.get('text')

        if not user_input:
            return JsonResponse({'error': 'No input provided'}, status=400)

        bot_response = get_bot_response(user_input)

        return JsonResponse({'data': {'text': bot_response}})

    return render(request, 'chatbot.html', {'chats': []})

def get_bot_response(user_input):
    genai.configure(api_key=settings.GEMINI_APIKEY)

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=genai.types.GenerationConfig(
            temperature=0.1,
            max_output_tokens=300,
        ),
        system_instruction=(
            "Provide personalized, actionable financial advice and saving tips based on the user's current situation. "
            "Focus on offering clear, concise, and practical steps for achieving financial stability and meeting their financial goals. "
            "Avoid technical jargon and offer suggestions that are easy to understand and implement. "
            "Tailor the advice to the user's needs, and ensure it is focused on improving both short-term financial health and long-term stability. "
            "Keep responses short and simple as possible with a max limit of 300 words."
        )
    )

    response = model.generate_content([user_input])

    try:
        bot_response = response.text
    except AttributeError:
        bot_response = "Sorry, I couldn't generate a response."

    return bot_response