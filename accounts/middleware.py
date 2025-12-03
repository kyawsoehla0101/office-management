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

from .models import OfficeDevice


class OfficeDeviceMiddleware(MiddlewareMixin):
    COOKIE_NAME = "office_device_id"

    def process_request(self, request):

        # ---- FIX: always make path a string ----
        path = getattr(request, "path", "") or ""
        # 1) BYPASS admin
        if path.startswith("/admin/"):
            return None

        # 2) BYPASS static/media/favicons
        if (
            path.startswith("/static/")
            or path.startswith("/media/")
            or path.startswith("/favicon.")
        ):
            return None

        # 3) BYPASS device-not-allowed page itself
        # (NO reverse() USED → avoids Render crash)
        if "device/not-allowed" in path:
            return None

        # 4) Read device_id from cookie
        device_id = request.COOKIES.get(self.COOKIE_NAME)
        request.new_device_id = None

        if not device_id:
            device_id = uuid.uuid4().hex
            request.new_device_id = device_id

        # 5) Get or create device record
        device, _ = OfficeDevice.objects.get_or_create(
            device_id=device_id,
            defaults={"is_allowed": False},
        )

        # 6) Update tracking
        device.last_seen = timezone.now()
        device.last_ip = self._get_ip(request)
        if request.user.is_authenticated:
            device.last_user = request.user
        device.save()

        # 7) Attach to request for view usage
        request.office_device = device

        # 8) NOT ALLOWED → redirect
        if not device.is_allowed:
            return redirect("/device/not-allowed/")

        return None

    def process_response(self, request, response):

        device_id = getattr(request, "new_device_id", None)

        if device_id and hasattr(response, "set_cookie"):

            # secure flag auto-switch
            try:
                secure_flag = request.is_secure()
            except:
                secure_flag = False

            response.set_cookie(
                self.COOKIE_NAME,
                device_id,
                max_age=3600 * 24 * 365,
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
