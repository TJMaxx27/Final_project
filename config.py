import os

from dotenv import load_dotenv

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "default_user")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "default_password")
Authorization_key = os.getenv("Authorization_key", "default_key")
Phone = os.getenv("Phone", "default_phone")
test_project_id = os.getenv("test_project_id", "default_project_id")
company_id = os.getenv("company_id", "default_company_id")
