import random
import os
import uuid
from datetime import datetime


def generate_verification_code():
    return str(random.randint(100000, 999999))

def get_upload_path(instance, filename, file_type="files"):
    """
    Generate a structured path like:
    users/<user_id>/<file_type>/<filename_unique>
    """
    # Get extension
    ext = os.path.splitext(filename)[1].lower()


    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Unique name
    new_filename = f"{file_type}_{instance.id or "new"}_{date_str}{ext}"

    return os.path.join("users", str(instance.id or "temp"), file_type, new_filename)

def get_avatar_upload_path(instance, filename):
    return get_upload_path(instance, filename, file_type="avatar")

def get_banner_upload_path(instance, filename):
    return get_upload_path(instance, filename, file_type="banner")


def delete_old_file(instance, field_name):
    try:
        old_file = getattr(instance.__class__.objects.get(pk=instance.pk), field_name)
    except instance.__class__.DoesNotExist:
        return
    
    new_file = getattr(instance, field_name)
    if old_file and old_file != new_file and os.path.isfile(old_file.path):
        os.remove(old_file.path)