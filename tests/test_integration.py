import pytest
from decimal import Decimal
from uuid import UUID
from fastapi import status
from app.models.enums import OperationType


class TestIntegrationScenarios:
    """Integration test suite for complete user workflows."""

    @pytest.mark.asyncio
    async def test_complete_wallet_workflow(self, get_async_client):
        """Test complete wallet workflow: create -> deposit -> withdraw -> check balance."""
        client = get_async_client
        # Step 1: Create wallet with initial balance
        create_response = await client.post(
            "/api/v1/wallets",
            json={"balance": "100.00"},
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        wallet_data = create_response.json()["data"]
        wallet_id = wallet_data["id"]
        initial_balance = Decimal(wallet_data["balance"])
        assert initial_balance == Decimal("100.00")

        # Step 2: Make a deposit
        deposit_response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={
                "wallet_id": wallet_id,
                "amount": "50.25",
                "kind": OperationType.DEPOSIT.value,
            },
        )
        assert deposit_response.status_code == status.HTTP_201_CREATED

        deposit_data = deposit_response.json()["data"]
        assert deposit_data["wallet_id"] == wallet_id
        assert Decimal(deposit_data["amount"]) == Decimal("50.25")
        assert deposit_data["kind"] == OperationType.DEPOSIT.value

        # Step 3: Make a withdrawal
        withdraw_response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={
                "wallet_id": wallet_id,
                "amount": "25.50",
                "kind": OperationType.WITHDRAW.value,
            },
        )
        assert withdraw_response.status_code == status.HTTP_201_CREATED

        withdraw_data = withdraw_response.json()["data"]
        assert withdraw_data["wallet_id"] == wallet_id
        assert Decimal(withdraw_data["amount"]) == Decimal("25.50")
        assert withdraw_data["kind"] == OperationType.WITHDRAW.value

        # Step 4: Check final wallet balance
        get_response = await client.get(f"/api/v1/wallets/{wallet_id}")
        assert get_response.status_code == status.HTTP_200_OK

        final_wallet_data = get_response.json()["data"]
        final_balance = Decimal(final_wallet_data["balance"])

        # Expected balance: 100.00 + 50.25 - 25.50 = 124.75
        expected_balance = initial_balance + Decimal("50.25") - Decimal("25.50")
        assert final_balance == expected_balance

    @pytest.mark.asyncio
    async def test_multiple_wallets_operations(self, get_async_client):
        """Test operations across multiple wallets."""
        client = get_async_client
        # Create multiple wallets
        wallets = []
        for i in range(3):
            response = await client.post(
                "/api/v1/wallets",
                json={"balance": f"{100 + i * 50}.00"},
            )
            assert response.status_code == status.HTTP_201_CREATED
            wallets.append(response.json()["data"])

        # Perform operations on each wallet
        for i, wallet in enumerate(wallets):
            wallet_id = wallet["id"]

            # Deposit different amounts
            deposit_response = await client.post(
                f"/api/v1/wallets/{wallet_id}/operation",
                json={
                    "wallet_id": wallet_id,
                    "amount": f"{10 + i * 5}.00",
                    "kind": OperationType.DEPOSIT.value,
                },
            )
            assert deposit_response.status_code == status.HTTP_201_CREATED

            # Verify the operation
            deposit_data = deposit_response.json()["data"]
            assert deposit_data["wallet_id"] == wallet_id
            assert Decimal(deposit_data["amount"]) == Decimal(f"{10 + i * 5}.00")

    @pytest.mark.asyncio
    async def test_concurrent_operations_same_wallet(self, get_async_client):
        """Test concurrent operations on the same wallet."""
        client = get_async_client
        # Create wallet
        create_response = await client.post(
            "/api/v1/wallets",
            json={"balance": "1000.00"},
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        wallet_id = create_response.json()["data"]["id"]

        # Perform multiple concurrent deposits
        import asyncio

        async def make_deposit(amount):
            return await client.post(
                f"/api/v1/wallets/{wallet_id}/operation",
                json={
                    "wallet_id": wallet_id,
                    "amount": str(amount),
                    "kind": OperationType.DEPOSIT.value,
                },
            )

        # Make 5 concurrent deposits of 10.00 each
        tasks = [make_deposit(10.00) for _ in range(5)]
        responses = await asyncio.gather(*tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()["data"]
            assert Decimal(data["amount"]) == Decimal("10.00")
            assert data["kind"] == OperationType.DEPOSIT.value

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, get_async_client):
        """Test error recovery in a workflow."""
        client = get_async_client
        # Step 1: Try to get non-existent wallet (should fail)
        non_existent_id = str(UUID("550e8400-e29b-41d4-a716-446655440000"))
        get_response = await client.get(f"/api/v1/wallets/{non_existent_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

        # Step 2: Create the wallet
        create_response = await client.post(
            "/api/v1/wallets",
            json={"balance": "50.00"},
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        wallet_id = create_response.json()["data"]["id"]

        # Step 3: Now get the wallet (should succeed)
        get_response = await client.get(f"/api/v1/wallets/{wallet_id}")
        assert get_response.status_code == status.HTTP_200_OK

        wallet_data = get_response.json()["data"]
        assert wallet_data["id"] == wallet_id
        assert Decimal(wallet_data["balance"]) == Decimal("50.00")

    @pytest.mark.asyncio
    async def test_large_number_operations(self, get_async_client):
        """Test operations with large numbers."""
        client = get_async_client
        # Create wallet with large balance
        large_balance = "999999999.99"
        create_response = await client.post(
            "/api/v1/wallets",
            json={"balance": large_balance},
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        wallet_id = create_response.json()["data"]["id"]
        assert Decimal(create_response.json()["data"]["balance"]) == Decimal(
            large_balance,
        )

        # Perform large deposit
        large_deposit = "1000000.00"
        deposit_response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={
                "wallet_id": wallet_id,
                "amount": large_deposit,
                "kind": OperationType.DEPOSIT.value,
            },
        )
        assert deposit_response.status_code == status.HTTP_201_CREATED

        deposit_data = deposit_response.json()["data"]
        assert Decimal(deposit_data["amount"]) == Decimal(large_deposit)

    @pytest.mark.asyncio
    async def test_mixed_operation_types_workflow(self, get_async_client):
        """Test workflow with mixed operation types."""
        client = get_async_client
        # Create wallet
        create_response = await client.post(
            "/api/v1/wallets",
            json={"balance": "200.00"},
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        wallet_id = create_response.json()["data"]["id"]

        # Perform mixed operations
        operations = [
            ("50.00", OperationType.DEPOSIT.value),
            ("25.00", OperationType.WITHDRAW.value),
            ("100.00", OperationType.DEPOSIT.value),
            ("75.00", OperationType.WITHDRAW.value),
        ]

        for amount, operation_type in operations:
            response = await client.post(
                f"/api/v1/wallets/{wallet_id}/operation",
                json={
                    "wallet_id": wallet_id,
                    "amount": amount,
                    "kind": operation_type,
                },
            )
            assert response.status_code == status.HTTP_201_CREATED

            data = response.json()["data"]
            assert Decimal(data["amount"]) == Decimal(amount)
            assert data["kind"] == operation_type
