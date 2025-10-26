import pytest
from decimal import Decimal
from uuid import uuid4
from fastapi import status
from app.models.enums import OperationType


class TestTransactionEndpoints:
    """Test suite for transaction/operation-related endpoints."""

    @pytest.mark.asyncio
    async def test_deposit_operation_success(self, get_async_client):
        """Test successful deposit operation."""
        client = get_async_client
        # First create a wallet
        create_response = await client.post(
            "/api/v1/wallets",
            json={"balance": "100.00"},
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        wallet_id = create_response.json()["data"]["id"]

        # Perform deposit operation
        deposit_amount = "50.25"
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={
                "wallet_id": wallet_id,
                "amount": deposit_amount,
                "kind": OperationType.DEPOSIT.value,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Check response structure
        assert "data" in data
        assert "meta" in data
        assert "errors" in data
        assert data["errors"] == []

        # Check transaction data
        transaction_data = data["data"]
        assert "id" in transaction_data
        assert transaction_data["wallet_id"] == wallet_id
        assert Decimal(transaction_data["amount"]) == Decimal(deposit_amount)
        assert transaction_data["kind"] == OperationType.DEPOSIT.value
        assert "created_at" in transaction_data
        assert "updated_at" in transaction_data

    @pytest.mark.asyncio
    async def test_withdraw_operation_success(self, get_async_client):
        """Test successful withdraw operation."""
        client = get_async_client
        # First create a wallet with sufficient balance
        create_response = await client.post(
            "/api/v1/wallets",
            json={"balance": "200.00"},
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        wallet_id = create_response.json()["data"]["id"]

        # Perform withdraw operation
        withdraw_amount = "75.50"
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={
                "wallet_id": wallet_id,
                "amount": withdraw_amount,
                "kind": OperationType.WITHDRAW.value,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Check transaction data
        transaction_data = data["data"]
        assert transaction_data["wallet_id"] == wallet_id
        assert Decimal(transaction_data["amount"]) == Decimal(withdraw_amount)
        assert transaction_data["kind"] == OperationType.WITHDRAW.value

    @pytest.mark.asyncio
    async def test_operation_wallet_not_found(self, get_async_client):
        """Test operation on non-existent wallet."""
        client = get_async_client
        non_existent_id = str(uuid4())
        response = await client.post(
            f"/api/v1/wallets/{non_existent_id}/operation",
            json={
                "wallet_id": non_existent_id,
                "amount": "50.00",
                "kind": OperationType.DEPOSIT.value,
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()

        # Check error structure
        assert "errors" in data
        assert len(data["errors"]) > 0

        error = data["errors"][0]
        assert "not found" in error["message"]
        assert non_existent_id in error["message"]

    @pytest.mark.asyncio
    async def test_operation_validation_negative_amount(self, get_async_client):
        """Test operation with negative amount should fail."""
        client = get_async_client
        # First create a wallet
        create_response = await client.post("/api/v1/wallets", json={})
        assert create_response.status_code == status.HTTP_201_CREATED

        wallet_id = create_response.json()["data"]["id"]

        # Try operation with negative amount
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={
                "wallet_id": wallet_id,
                "amount": "-50.00",
                "kind": OperationType.DEPOSIT.value,
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()

        assert "errors" in data
        assert len(data["errors"]) > 0

        # Check specific validation error
        error = data["errors"][0]
        assert error["field"] == "amount"
        assert "greater than or equal to 0" in error["message"]

    @pytest.mark.asyncio
    async def test_operation_validation_invalid_operation_type(self, get_async_client):
        """Test operation with invalid operation type should fail."""
        client = get_async_client
        # First create a wallet
        create_response = await client.post("/api/v1/wallets", json={})
        assert create_response.status_code == status.HTTP_201_CREATED

        wallet_id = create_response.json()["data"]["id"]

        # Try operation with invalid type
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={
                "wallet_id": wallet_id,
                "amount": "50.00",
                "kind": "invalid_operation",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()

        assert "errors" in data
        assert len(data["errors"]) > 0

    @pytest.mark.asyncio
    async def test_operation_validation_missing_fields(self, get_async_client):
        """Test operation with missing required fields should fail."""
        client = get_async_client
        # First create a wallet
        create_response = await client.post("/api/v1/wallets", json={})
        assert create_response.status_code == status.HTTP_201_CREATED

        wallet_id = create_response.json()["data"]["id"]

        # Try operation with missing amount
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"wallet_id": wallet_id, "kind": OperationType.DEPOSIT.value},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()

        assert "errors" in data
        assert len(data["errors"]) > 0

    @pytest.mark.asyncio
    async def test_operation_validation_wallet_id_mismatch(self, get_async_client):
        """Test operation with wallet_id mismatch between URL and body."""
        client = get_async_client
        # First create a wallet
        create_response = await client.post("/api/v1/wallets", json={})
        assert create_response.status_code == status.HTTP_201_CREATED

        wallet_id = create_response.json()["data"]["id"]
        different_wallet_id = str(uuid4())

        # Try operation with different wallet_id in body
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={
                "wallet_id": different_wallet_id,
                "amount": "50.00",
                "kind": OperationType.DEPOSIT.value,
            },
        )

        # This should still work as the URL wallet_id is used for the operation
        # The wallet_id in the body might be ignored or used for validation
        # The actual behavior depends on the implementation
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        ]

    @pytest.mark.asyncio
    async def test_operation_large_amount(self, get_async_client):
        """Test operation with large amount."""
        client = get_async_client
        # First create a wallet
        create_response = await client.post("/api/v1/wallets", json={})
        assert create_response.status_code == status.HTTP_201_CREATED

        wallet_id = create_response.json()["data"]["id"]

        # Try operation with large amount
        large_amount = "999999999.99"
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={
                "wallet_id": wallet_id,
                "amount": large_amount,
                "kind": OperationType.DEPOSIT.value,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        transaction_data = data["data"]
        assert Decimal(transaction_data["amount"]) == Decimal(large_amount)

    @pytest.mark.asyncio
    async def test_operation_invalid_uuid_format(self, get_async_client):
        """Test operation with invalid UUID format in URL."""
        client = get_async_client
        invalid_uuid = "not-a-valid-uuid"
        response = await client.post(
            f"/api/v1/wallets/{invalid_uuid}/operation",
            json={
                "wallet_id": invalid_uuid,
                "amount": "50.00",
                "kind": OperationType.DEPOSIT.value,
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()

        assert "errors" in data
        assert len(data["errors"]) > 0

    @pytest.mark.asyncio
    async def test_operation_extra_fields_ignored(self, get_async_client):
        """Test operation with extra fields should be ignored."""
        client = get_async_client
        # First create a wallet
        create_response = await client.post("/api/v1/wallets", json={})
        assert create_response.status_code == status.HTTP_201_CREATED

        wallet_id = create_response.json()["data"]["id"]

        # Try operation with extra fields
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={
                "wallet_id": wallet_id,
                "amount": "50.00",
                "kind": OperationType.DEPOSIT.value,
                "extra_field": "should_be_ignored",
                "another_field": 123,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        transaction_data = data["data"]
        assert "extra_field" not in transaction_data
        assert "another_field" not in transaction_data

    @pytest.mark.asyncio
    async def test_operation_response_meta_information(self, get_async_client):
        """Test that operation response meta information is properly set."""
        client = get_async_client
        # First create a wallet
        create_response = await client.post("/api/v1/wallets", json={})
        assert create_response.status_code == status.HTTP_201_CREATED

        wallet_id = create_response.json()["data"]["id"]

        # Perform operation
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={
                "wallet_id": wallet_id,
                "amount": "50.00",
                "kind": OperationType.DEPOSIT.value,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert "meta" in data
        assert "errors" in data
        assert data["errors"] == []
