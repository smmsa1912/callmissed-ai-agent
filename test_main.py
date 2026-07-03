import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

# Import your FastAPI app
from main import app

# Initialize the test client
client = TestClient(app)


def test_serve_index():
    """Test that the frontend HTML is served correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_chat_validation_error():
    """Test that the chat endpoint rejects requests without a message."""
    response = client.post("/chat", json={})
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"


def test_image_validation_error():
    """Test that the image endpoint rejects requests without a prompt."""
    response = client.post("/image", json={})
    assert response.status_code == 422


@patch("main.cm_client.images.generate", new_callable=AsyncMock)
def test_image_generation_success(mock_generate):
    """
    Test the image generation endpoint with a mocked CallMissed client
    so we don't actually hit the external API during tests.
    """
    # 1. Setup a fake response object that mimics the OpenAI SDK structure
    mock_image_data = MagicMock()
    mock_image_data.url = "https://fake-url.com/generated-image.png"
    mock_generate.return_value.data = [mock_image_data]

    # 2. Make the request to your local API
    response = client.post("/image", json={"prompt": "A test image"})

    # 3. Assert the results
    assert response.status_code == 200
    assert response.json() == {"url": "https://fake-url.com/generated-image.png"}

    # 4. Verify your backend actually called the CallMissed client
    mock_generate.assert_called_once()