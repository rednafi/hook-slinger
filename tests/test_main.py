from fastapi.routing import APIRouter
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app import main


def test_app_router():
    """Test Fastapi app router registration."""

    # Check that the API router has been registered properly.
    assert isinstance(main.app.router, APIRouter)


def test_app_middleware():
    """Test Fastapi app middleware config. The expected
    'main.app.user_middleware' should look like this:

    ```
    >>> main.app.user_middleware
    >>> Middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True,   allow_methods=['*'], allow_headers=['*'])
    ```
    """

    # Check that the middleware settings were properly registered to the app.

    user_middleware = main.app.user_middleware.pop()

    assert user_middleware.__class__ == Middleware
    assert user_middleware.__dict__ == {
        "cls": CORSMiddleware,
        "options": {
            "allow_origins": ["*"],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        },
    }
