import sys

sys.path.append("../backend")

from fastapi import FastAPI
from mangum import Mangum

from backend.main import app as fastapi_app

# Handler for AWS Lambda/Vercel
handler = Mangum(fastapi_app)
