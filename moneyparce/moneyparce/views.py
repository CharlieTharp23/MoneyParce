import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from django.http import HttpResponse
from django.core.mail import send_mail

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


def test_email(request):
    try:
        user_info = request.session.get("user", {})
        user_email = user_info.get("userinfo", {}).get("email")
        recipient_email = user_email if user_email else "your-test-email@example.com"
        
        subject = 'Test Email from MoneyParce'
        message = 'This is a test email sent from your Django application.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [recipient_email]
        
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        return HttpResponse(f"Test email sent successfully to {recipient_email}! Check your inbox.")
    except Exception as e:
        return HttpResponse(f"Failed to send email. Error: {str(e)}")