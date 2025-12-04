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
from django.shortcuts import redirect
from django.utils import timezone
from .models import OfficeDevice

class OfficeDeviceMiddleware(MiddlewareMixin):
    COOKIE_NAME = "device_id"

    def process_request(self, request):
        path = request.path or ""

        # Allow safe URLs
        if (
            path.startswith("/static/")
            or path.startswith("/media/")
            or path.startswith("/admin/")
            # or path == "/device/not-allowed/"
        ):
            return None

        # -------------------------
        # 1️⃣ Read cookie
        # -------------------------
        device_id = request.COOKIES.get(self.COOKIE_NAME)

        if not device_id:
            device_id = uuid.uuid4().hex
            request.new_device_id = device_id  # will be written in response

        # -------------------------
        # 2️⃣ Load or create device record
        # -------------------------
        device, created = OfficeDevice.objects.get_or_create(
            device_id=device_id,
            defaults={"is_allowed": False}
        )

        # -------------------------
        # 3️⃣ Update tracking (IP + last seen)
        # -------------------------
        device.last_seen = timezone.now()
        device.last_ip = self._get_ip(request)

        if request.user.is_authenticated:
            device.last_user = request.user

        device.save()

        # -------------------------
        # 4️⃣ Attach for templates and views
        # -------------------------
        request.device_id = device_id
        request.office_device = device
 

        # -------------------------
        # 5️⃣ Block if not allowed
        # -------------------------

        if path == "/device/not-allowed/":
            return None

        if not device.is_allowed:
            return redirect("/device/not-allowed/")

        return None

    def process_response(self, request, response):
        # Set cookie only for new devices
        if hasattr(request, "new_device_id") and hasattr(response, "set_cookie"):
            response.set_cookie(
                self.COOKIE_NAME,
                request.new_device_id,
                max_age=60 * 60 * 24 * 365,
                httponly=True,
                samesite="Lax"
            )
        return response

    def _get_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

