import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))
from notification_service import (
    NotificationTemplate, NotificationChannel, TemplateRenderer,
    ChannelRouter, EmailProvider, SmsProvider, PushProvider
)


def test_template_rendering_success():
    template = NotificationTemplate(
        template_id="t1",
        channel=NotificationChannel.EMAIL,
        name="Welcome Email",
        subject="Welcome {{name}}!",
        body="Hello {{name}}, your balance is {{balance}}.",
        required_variables=["name", "balance"]
    )
    
    variables = {"name": "Alice", "balance": "100"}
    renderer = TemplateRenderer()
    
    result = renderer.render(template, variables)
    assert result.subject == "Welcome Alice!"
    assert result.body == "Hello Alice, your balance is 100."


def test_template_rendering_missing_variable():
    template = NotificationTemplate(
        template_id="t2",
        channel=NotificationChannel.SMS,
        name="Alert SMS",
        subject=None,
        body="Alert: {{issue}}",
        required_variables=["issue"]
    )
    
    variables = {}
    renderer = TemplateRenderer()
    
    with pytest.raises(ValueError, match="Missing required variable: issue"):
        renderer.render(template, variables)


def test_channel_router_fallback():
    router = ChannelRouter()
    
    primary_email = EmailProvider("PrimaryEmail")
    fallback_email = EmailProvider("FallbackEmail")
    
    router.register_provider(primary_email)
    router.register_provider(fallback_email)
    
    # Both are healthy, should return first one (PrimaryEmail)
    provider = router.get_provider(NotificationChannel.EMAIL)
    assert provider == primary_email
    
    # Mark primary as unhealthy
    primary_email._healthy = False
    
    # Now it should return fallback email
    provider2 = router.get_provider(NotificationChannel.EMAIL)
    assert provider2 == fallback_email


def test_channel_router_all_unhealthy():
    router = ChannelRouter()
    
    provider1 = SmsProvider("Sms1")
    provider1._healthy = False
    
    router.register_provider(provider1)
    
    # Returns first one anyway if all are unhealthy
    provider = router.get_provider(NotificationChannel.SMS)
    assert provider == provider1


def test_channel_router_missing_channel():
    router = ChannelRouter()
    
    with pytest.raises(ValueError, match="No providers for channel: NotificationChannel.PUSH"):
        router.get_provider(NotificationChannel.PUSH)

