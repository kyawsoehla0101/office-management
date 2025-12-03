from base.models import SystemSettings

class DynamicSessionTimeoutMiddleware:
    """
    Updates session timeout dynamically from DB
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        settings_obj, _ = SystemSettings.objects.get_or_create(id=1)
        timeout_minutes = settings_obj.session_timeout
        request.session.set_expiry(timeout_minutes * 60)  # convert to seconds
        response = self.get_response(request)
        return response


# accounts/middleware.py

import uuid

from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse

from .models import OfficeDevice


class OfficeDeviceMiddleware(MiddlewareMixin):
    COOKIE_NAME = "office_device_id"

    def process_request(self, request):
        """
        Every request မှာ device ကိုစစ်မယ်
        - admin, static, media, favicon, device-not-allowed ကို bypass
        - Cookie ထဲက device_id မရှိရင် သစ်သစ် generate
        - OfficeDevice ကို get_or_create
        - is_allowed=False ဆိုရင် device_not_allowed သို့ redirect
        """

        path = request.path

        # 1) ADMIN bypass (Admin ကို Device မပိတ်ချင်ရင်)
        if path.startswith("/admin/"):
            return None

        # 2) STATIC/MEDIA/favicon/device-not-allowed bypass
        not_allowed_url = reverse("device_not_allowed")
        if (
            path.startswith("/static/")
            or path.startswith("/media/")
            or path.startswith("/favicon.")
            or path == not_allowed_url
        ):
            return None

        # 3) Cookie ထဲက device_id ယူမယ်
        device_id = request.COOKIES.get(self.COOKIE_NAME)
        request.new_device_id = None

        if not device_id:
            # ပထမဆုံးလာတဲ့ browser/device → UUID အသစ် generate
            device_id = uuid.uuid4().hex
            request.new_device_id = device_id

        # 4) OfficeDevice record ကို get_or_create
        device, _ = OfficeDevice.objects.get_or_create(
            device_id=device_id,
            defaults={"is_allowed": False},
        )

        # 5) Tracking fields update
        device.last_seen = timezone.now()
        device.last_ip = self._get_ip(request)
        if request.user.is_authenticated:
            device.last_user = request.user
        device.save()

        # 6) request object မှာ attach (view/device_not_allowed အတွက်)
        request.office_device = device

        # 7) Device not allowed ဖြစ်ရင် device-not-allowed သို့ redirect
        if not device.is_allowed:
            return redirect("device_not_allowed")

        # 8) allow → view ဆီသွား
        return None

    def process_response(self, request, response):
        """
        Cookie set logic:
        - Localhost / HTTP → secure=False
        - HTTPS (Render / office.arakkha.tech) → secure=True
        (request.is_secure() ကိုအလိုအလျောက်သုံး)
        """
        device_id = getattr(request, "new_device_id", None)

        if device_id and hasattr(response, "set_cookie"):
            secure_flag = False
            try:
                secure_flag = request.is_secure()
            except Exception:
                secure_flag = False

            # Cookie domain ကို မသတ်မှတ်ပါနဲ့ (host အလိုလို သွားမယ် → Render / localhost နှစ်မျိုးလုံးအလုပ်လုပ်)
            response.set_cookie(
                self.COOKIE_NAME,
                device_id,
                max_age=3600 * 24 * 365,  # 1 year
                httponly=True,
                secure=secure_flag,
                samesite="Lax",
            )

        return response

    def _get_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
