import pytest
from unittest.mock import patch
from src.services.qr import generate_qr_and_upload_to_cloudinary

@pytest.mark.asyncio
async def test_generate_qr_and_upload_to_cloudinary_picture():
    url = "https://example.com"
    picture = {
        "folder": "test_folder",
        "public_id": "test_public_id",
        "version": "test_version"
    }

    expected_qr_url = "https://cloudinary.com/qrcode/test_qr"
    expected_upload_response = {
        "public_id": "test_public_id",
        "version": "test_version"
    }

    with patch("src.services.qr.generate_random_string", return_value="test_qr"), \
         patch("src.services.qr.cloudinary.uploader.upload", veturn_value=expected_upload_response) as mock_cloudinary_upload, \
         patch("src.services.qr.cloudinary.CloudinaryImage.build_url", return_value=expected_qr_url) as mock_build_url:

        qr_url = await generate_qr_and_upload_to_cloudinary(url, picture)

        assert qr_url == expected_qr_url
        mock_cloudinary_upload.assert_called_once()
        mock_build_url.assert_called_once_with(version='test_version')

@pytest.mark.asyncio
async def test_generate_qr_and_upload_to_cloudinary_any_url():
    url = "https://example.com"

    expected_qr_url = "https://cloudinary.com/qrcode/test_qr"
    expected_upload_response = {
        "public_id": "test_public_id",
        "version": "test_version"
    }

    with patch("src.services.qr.generate_random_string", return_value="test_qr"), \
         patch("src.services.qr.cloudinary.uploader.upload", return_value=expected_upload_response) as mock_cloudinary_upload, \
         patch("src.services.qr.cloudinary.CloudinaryImage.build_url", return_value=expected_qr_url) as mock_build_url:

        qr_url = await generate_qr_and_upload_to_cloudinary(url)

        assert qr_url == expected_qr_url
        mock_cloudinary_upload.assert_called_once()
        mock_build_url.assert_called_once_with(version='test_version')

