import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import app
from fastapi.openapi.utils import get_openapi

try:
    schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    print("OpenAPI schema generated successfully!")
except Exception as e:
    import traceback
    print("Failed to generate OpenAPI schema:")
    traceback.print_exc()
    sys.exit(1)
