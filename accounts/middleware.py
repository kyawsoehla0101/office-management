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
from django.conf import settings

from .models import OfficeDevice

class OfficeDeviceMiddleware(MiddlewareMixin):
    COOKIE_NAME = "office_device_id"

    def process_request(self, request):
        path = request.path

        # allow admin always
        if path.startswith("/admin/"):
            return None

        # allow superuser
        if request.user.is_authenticated and request.user.is_superuser:
            return None

        # bypass static + media + favicon
        if (
            path.startswith("/static/")
            or path.startswith("/media/")
            or path.startswith("/favicon.")
            or path.startswith("/device/not-allowed/")
        ):
            return None

        # read cookie
        device_id = request.COOKIES.get(self.COOKIE_NAME)
        request.new_device_id = None

        if not device_id:
            # generate device ID for first time
            device_id = uuid.uuid4().hex
            request.new_device_id = device_id

        device, _ = OfficeDevice.objects.get_or_create(
            device_id=device_id,
            defaults={"is_allowed": False, "last_ip": self._get_ip(request)},
        )

        # update tracking fields
        device.last_seen = timezone.now()
        device.last_ip = self._get_ip(request)
        if request.user.is_authenticated:
            device.last_user = request.user
        device.save()

        request.office_device = device

        # restricted?
        if not device.is_allowed:
            return redirect("device_not_allowed")

        return None


    def process_response(self, request, response):
        """
        Secure cookie auto-switch:
        - DEV (localhost, 127.0.0.1) → secure=False
        - PROD (https://office.arakkha.tech) → secure=True
        """

        device_id = getattr(request, "new_device_id", None)
        if device_id and hasattr(response, "set_cookie"):

            secure_flag = False
            domain_value = None

            if settings.IS_PROD:
                secure_flag = True
                domain_value = "office.arakkha.tech"

            response.set_cookie(
                self.COOKIE_NAME,
                device_id,
                max_age=3600 * 24 * 365,
                httponly=True,
                secure=secure_flag,
                samesite="Lax",
                domain=domain_value,
            )

        return response


    def _get_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
