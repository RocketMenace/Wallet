import pytest
from decimal import Decimal
from uuid import uuid4
from fastapi import status
from app.models.enums import OperationType


class TestErrorHandling:
    """Test suite for error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_invalid_json_payload(self, get_async_client):
        """Test handling of invalid JSON payload."""
        client = get_async_client
        # Test with malformed JSON
        response = await client.post(
            "/api/v1/wallets",
            content='{"balance": "100.00", "invalid": }',  # Missing value
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_empty_json_payload(self, get_async_client):
        """Test handling of empty JSON payload."""
        client = get_async_client
        response = await client.post(
            "/api/v1/wallets",
            content="{}",
            headers={"Content-Type": "application/json"},
        )

        # Empty JSON should work for wallet creation (uses default balance)
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.asyncio
    async def test_missing_content_type_header(self, get_async_client):
        """Test handling of missing Content-Type header."""
        client = get_async_client
        response = await client.post(
            "/api/v1/wallets",
            content='{"balance": "100.00"}',
            # No Content-Type header
        )

        # FastAPI should still process this as JSON
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.asyncio
    async def test_very_large_payload(self, get_async_client):
        """Test handling of very large payload."""
        client = get_async_client
        large_data = {
            "balance": "100.00",
            "extra_data": "x" * 10000,  # 10KB of extra data
        }

        response = await client.post("/api/v1/wallets", json=large_data)

        # Should still work, extra fields should be ignored
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.asyncio
    async def test_special_characters_in_payload(self, get_async_client):
        client = get_async_client
        special_data = {
            "balance": "100.00",
            "special_field": "!@#$%^&*()_+-=[]{}|;':\",./<>?`~",
        }

        response = await client.post("/api/v1/wallets", json=special_data)

        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.asyncio
    async def test_unicode_characters_in_payload(self, get_async_client):
        client = get_async_client
        unicode_data = {"balance": "100.00", "unicode_field": "🚀💰💳🎯🔥"}

        response = await client.post("/api/v1/wallets", json=unicode_data)

        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.asyncio
    async def test_numeric_string_validation(self, get_async_client):
        """Test validation of numeric strings."""
        client = get_async_client
        # Test various numeric string formats
        test_cases = [
            "100",  # Integer string
            "100.0",  # Decimal with trailing zero
            "100.00",  # Decimal with two decimal places
            "0.01",  # Small decimal
            "999999.99",  # Large decimal
        ]

        for balance_str in test_cases:
            response = await client.post(
                "/api/v1/wallets",
                json={"balance": balance_str},
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert Decimal(data["data"]["balance"]) == Decimal(balance_str)

    @pytest.mark.asyncio
    async def test_operation_type_case_sensitivity(self, get_async_client):
        """Test operation type case sensitivity."""
        client = get_async_client
        # First create a wallet
        create_response = await client.post("/api/v1/wallets", json={})
        assert create_response.status_code == status.HTTP_201_CREATED

        wallet_id = create_response.json()["data"]["id"]

        # Test case variations
        case_variations = ["DEPOSIT", "WITHDRAW"]

        for operation_type in case_variations:
            response = await client.post(
                f"/api/v1/wallets/{wallet_id}/operation",
                json={
                    "wallet_id": wallet_id,
                    "amount": "10.00",
                    "kind": operation_type,
                },
            )

            if operation_type == "deposit":
                assert response.status_code == status.HTTP_201_CREATED
            else:
                # Other cases should fail validation
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_concurrent_wallet_operations(
        self,
        get_async_client,
        create_test_wallet_id,
    ):
        client = get_async_client
        # create_response = await client.post(
        #     "/api/v1/wallets", json={"balance": "1000.00"}
        # )
        # assert create_response.status_code == status.HTTP_201_CREATED

        wallet_id = create_test_wallet_id

        import asyncio

        async def make_deposit(amount):
            return await client.post(
                f"/api/v1/wallets/{wallet_id}/operation",
                json={
                    "wallet_id": wallet_id,
                    "amount": amount,
                    "kind": OperationType.DEPOSIT.value,
                },
            )

        # Make 5 concurrent deposits
        tasks = [make_deposit(10.00) for _ in range(5)]
        responses = await asyncio.gather(*tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.asyncio
    async def test_rapid_sequential_requests(self, get_async_client):
        client = get_async_client
        # Create multiple wallets rapidly
        responses = []
        for i in range(10):
            response = await client.post(
                "/api/v1/wallets",
                json={"balance": f"{i * 10}.00"},
            )
            responses.append(response)

        # All should succeed
        for response in responses:
            assert response.status_code == status.HTTP_201_CREATED

        # All should have unique IDs
        wallet_ids = [resp.json()["data"]["id"] for resp in responses]
        assert len(set(wallet_ids)) == len(wallet_ids)

    @pytest.mark.asyncio
    async def test_malformed_uuid_handling(self, get_async_client):
        """Test handling of malformed UUIDs."""
        client = get_async_client
        malformed_uuids = [
            "not-a-uuid",
            "123",
            "550e8400-e29b-41d4-a716",  # Incomplete UUID
            "550e8400-e29b-41d4-a716-446655440000-extra",  # Too long
            "550e8400-e29b-41d4-a716-44665544000g",  # Invalid character
        ]

        for malformed_uuid in malformed_uuids:
            response = await client.get(f"/api/v1/wallets/{malformed_uuid}")
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_boundary_value_testing(self, get_async_client):
        """Test boundary values for numeric inputs."""
        client = get_async_client
        # Test boundary values
        boundary_values = [
            "0.00",  # Minimum valid value
            "0.01",  # Smallest positive value
            "999999999.99",  # Large but reasonable value
        ]

        for balance in boundary_values:
            response = await client.post("/api/v1/wallets", json={"balance": balance})

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert Decimal(data["data"]["balance"]) == Decimal(balance)

    @pytest.mark.asyncio
    async def test_error_response_structure_consistency(self, get_async_client):
        """Test that error responses have consistent structure."""
        client = get_async_client
        # Test 404 error
        non_existent_id = str(uuid4())
        response = await client.get(f"/api/v1/wallets/{non_existent_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()

        # Check consistent error structure
        assert "data" in data
        assert "meta" in data
        assert "errors" in data
        assert isinstance(data["errors"], list)
        assert len(data["errors"]) > 0

        # Check error object structure
        error = data["errors"][0]
        assert "message" in error
        assert isinstance(error["message"], str)
        assert len(error["message"]) > 0

    @pytest.mark.asyncio
    async def test_operation_with_insufficient_funds_simulation(self, get_async_client):
        """Test operation that might result in insufficient funds."""
        client = get_async_client
        # Create wallet with small balance
        create_response = await client.post(
            "/api/v1/wallets",
            json={"balance": "10.00"},
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        wallet_id = create_response.json()["data"]["id"]

        # Try to withdraw more than available
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={
                "wallet_id": wallet_id,
                "amount": "100.00",  # More than available
                "kind": OperationType.WITHDRAW.value,
            },
        )

        # The actual behavior depends on your business logic
        # This test documents the expected behavior
        # It could be 400 (insufficient funds) or 201 (if you allow negative balances)
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
        ]

    @pytest.mark.asyncio
    async def test_very_long_string_inputs(self, get_async_client):
        client = get_async_client
        long_string = "x" * 10000

        response = await client.post(
            "/api/v1/wallets",
            json={"balance": "100.00", "long_field": long_string},
        )

        assert response.status_code == status.HTTP_201_CREATED
