"""Create wallet models

Creates wallets and transactions tables exactly matching SQLAlchemy models.

Revision ID: 0486503be796
Revises: 
Create Date: 2025-10-22 11:15:01.814590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0486503be796'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create wallet and transaction tables matching SQLAlchemy models."""
    
    # Create enum type for operation types
    op.execute("""
        CREATE TYPE operationtype AS ENUM ('deposit', 'withdraw');
    """)
    
    # Create wallets table
    op.execute("""
        CREATE TABLE wallets (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            balance NUMERIC(19, 4) NOT NULL DEFAULT 0.0000,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
    """)
    
    # Create transactions table
    op.execute("""
        CREATE TABLE transactions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            wallet_id UUID NOT NULL,
            amount NUMERIC(19, 4) NOT NULL,
            kind operationtype NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
            FOREIGN KEY (wallet_id) REFERENCES wallets(id) ON DELETE CASCADE
        );
    """)
    
    # Add check constraints from __table_args__
    op.execute("""
        ALTER TABLE wallets 
        ADD CONSTRAINT non_negative_balance 
        CHECK (balance >= 0);
    """)
    
    op.execute("""
        ALTER TABLE transactions 
        ADD CONSTRAINT positive_amount 
        CHECK (amount > 0);
    """)
    
    # Create indexes from model definitions
    op.execute("""
        CREATE INDEX ix_transactions_wallet_id 
        ON transactions(wallet_id);
    """)
    
    op.execute("""
        CREATE INDEX idx_transaction_wallet_created 
        ON transactions(wallet_id, created_at);
    """)


def downgrade() -> None:
    """Drop wallet and transaction tables."""
    
    # Drop tables (CASCADE handles foreign key constraints)
    op.execute("DROP TABLE IF EXISTS transactions CASCADE;")
    op.execute("DROP TABLE IF EXISTS wallets CASCADE;")
    
    # Drop enum type
    op.execute("DROP TYPE IF EXISTS operationtype;")
