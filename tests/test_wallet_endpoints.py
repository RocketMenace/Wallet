import pytest
from decimal import Decimal
from uuid import UUID, uuid4
from fastapi import status


class TestWalletEndpoints:
    """Test suite for wallet-related endpoints."""

    @pytest.mark.asyncio
    async def test_create_wallet_success_default_balance(self, get_async_client):
        client = get_async_client
        response = await client.post("/api/v1/wallets", json={})

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Check response structure
        assert "data" in data
        assert "meta" in data
        assert "errors" in data
        assert data["errors"] == []

        # Check wallet data
        wallet_data = data["data"]
        assert "id" in wallet_data
        assert "balance" in wallet_data
        assert "created_at" in wallet_data
        assert "updated_at" in wallet_data

        # Validate UUID format
        assert UUID(wallet_data["id"])

        # Check default balance
        assert Decimal(wallet_data["balance"]) == Decimal("0.00")

        # Check timestamps are present
        assert wallet_data["created_at"] is not None
        assert wallet_data["updated_at"] is not None

    @pytest.mark.asyncio
    async def test_create_wallet_success_custom_balance(self, get_async_client):
        """Test creating a wallet with custom initial balance."""
        client = get_async_client
        initial_balance = "100.50"
        response = await client.post(
            "/api/v1/wallets",
            json={"balance": initial_balance},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        wallet_data = data["data"]
        assert Decimal(wallet_data["balance"]) == Decimal(initial_balance)

    @pytest.mark.asyncio
    async def test_create_wallet_validation_negative_balance(self, get_async_client):
        """Test creating a wallet with negative balance should fail."""
        client = get_async_client
        response = await client.post("/api/v1/wallets", json={"balance": "-50.00"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()

        # Check error structure
        assert "errors" in data
        assert len(data["errors"]) > 0

        # Check specific validation error
        error = data["errors"][0]
        assert error["field"] == "balance"
        assert "greater than or equal to 0" in error["message"]
        assert error["input"] == "-50.00"  # Input is returned as string

    @pytest.mark.asyncio
    async def test_create_wallet_validation_invalid_balance_type(
        self,
        get_async_client,
    ):
        """Test creating a wallet with invalid balance type should fail."""
        client = get_async_client
        response = await client.post(
            "/api/v1/wallets",
            json={"balance": "not_a_number"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()

        assert "errors" in data
        assert len(data["errors"]) > 0

    @pytest.mark.asyncio
    async def test_create_wallet_validation_extra_fields(self, get_async_client):
        """Test creating a wallet with extra fields should be ignored."""
        client = get_async_client
        response = await client.post(
            "/api/v1/wallets",
            json={"balance": "50.00", "extra_field": "should_be_ignored"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        wallet_data = data["data"]
        assert Decimal(wallet_data["balance"]) == Decimal("50.00")
        assert "extra_field" not in wallet_data

    @pytest.mark.asyncio
    async def test_get_wallet_success(self, get_async_client):
        """Test retrieving an existing wallet."""
        client = get_async_client
        # First create a wallet
        create_response = await client.post(
            "/api/v1/wallets",
            json={"balance": "75.25"},
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        wallet_id = create_response.json()["data"]["id"]

        # Then retrieve it
        response = await client.get(f"/api/v1/wallets/{wallet_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check response structure
        assert "data" in data
        assert "meta" in data
        assert "errors" in data
        assert data["errors"] == []

        # Check wallet data
        wallet_data = data["data"]
        assert wallet_data["id"] == wallet_id
        assert Decimal(wallet_data["balance"]) == Decimal("75.25")
        assert "created_at" in wallet_data
        assert "updated_at" in wallet_data

    @pytest.mark.asyncio
    async def test_get_wallet_not_found(self, get_async_client):
        """Test retrieving a non-existent wallet."""
        client = get_async_client
        non_existent_id = str(uuid4())
        response = await client.get(f"/api/v1/wallets/{non_existent_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()

        # Check error structure
        assert "errors" in data
        assert len(data["errors"]) > 0

        error = data["errors"][0]
        assert "not found" in error["message"]
        assert non_existent_id in error["message"]

    @pytest.mark.asyncio
    async def test_get_wallet_invalid_uuid(self, get_async_client):
        """Test retrieving a wallet with invalid UUID format."""
        client = get_async_client
        invalid_uuid = "not-a-valid-uuid"
        response = await client.get(f"/api/v1/wallets/{invalid_uuid}")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()

        assert "errors" in data
        assert len(data["errors"]) > 0

    @pytest.mark.asyncio
    async def test_wallet_balance_precision(self, get_async_client):
        """Test wallet balance precision handling."""
        client = get_async_client
        # Test with high precision decimal
        high_precision_balance = "123.456789"
        response = await client.post(
            "/api/v1/wallets",
            json={"balance": high_precision_balance},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        wallet_data = data["data"]
        # The balance should be stored with database precision (NUMERIC(19, 2) = 2 decimal places)
        # So 123.456789 becomes 123.46
        expected_balance = "123.46"
        assert Decimal(wallet_data["balance"]) == Decimal(expected_balance)

    @pytest.mark.asyncio
    async def test_wallet_zero_balance(self, get_async_client):
        """Test creating a wallet with exactly zero balance."""
        client = get_async_client
        response = await client.post("/api/v1/wallets", json={"balance": "0.00"})

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        wallet_data = data["data"]
        assert Decimal(wallet_data["balance"]) == Decimal("0.00")

    @pytest.mark.asyncio
    async def test_wallet_large_balance(self, get_async_client):
        """Test creating a wallet with a large balance."""
        client = get_async_client
        large_balance = "999999999.99"
        response = await client.post("/api/v1/wallets", json={"balance": large_balance})

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        wallet_data = data["data"]
        assert Decimal(wallet_data["balance"]) == Decimal(large_balance)

    @pytest.mark.asyncio
    async def test_wallet_response_meta_information(self, get_async_client):
        """Test that response meta information is properly set."""
        client = get_async_client
        # Test create endpoint meta
        create_response = await client.post("/api/v1/wallets", json={})
        assert create_response.status_code == status.HTTP_201_CREATED

        create_data = create_response.json()
        assert "meta" in create_data
        # Meta should be empty for successful responses as per the implementation

        # Test get endpoint meta
        wallet_id = create_data["data"]["id"]
        get_response = await client.get(f"/api/v1/wallets/{wallet_id}")
        assert get_response.status_code == status.HTTP_200_OK

        get_data = get_response.json()
        assert "meta" in get_data
