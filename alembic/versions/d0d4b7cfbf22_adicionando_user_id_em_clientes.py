"""Adicionando user_id em clientes

Revision ID: d0d4b7cfbf22
Revises: 088d7ee48244
Create Date: 2026-05-11 20:14:51.110070

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0d4b7cfbf22'
down_revision: Union[str, Sequence[str], None] = '088d7ee48244'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. adiciona coluna permitindo NULL temporariamente
    op.add_column(
        'clientes',
        sa.Column('user_id', sa.Integer(), nullable=True)
    )

    # 2. preenche registros antigos
    # IMPORTANTE: precisa existir usuario com id=1
    op.execute(
        "UPDATE clientes SET user_id = 1 WHERE user_id IS NULL"
    )

    # 3. torna obrigatório
    op.alter_column(
        'clientes',
        'user_id',
        existing_type=sa.Integer(),
        nullable=False
    )

    # 4. cria foreign key
    op.create_foreign_key(
        'fk_clientes_user_id',
        'clientes',
        'usuarios',
        ['user_id'],
        ['id']
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        'fk_clientes_user_id',
        'clientes',
        type_='foreignkey'
    )

    op.drop_column('clientes', 'user_id')
