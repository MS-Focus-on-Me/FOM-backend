"""Add Emotion table

Revision ID: 6e47aa6d1bb5
Revises: cbcdd83f16a1
Create Date: 2025-06-04 03:56:30.410124

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e47aa6d1bb5'
down_revision: Union[str, None] = 'cbcdd83f16a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('emotions',
    sa.Column('emotion_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('diary_id', sa.Integer(), nullable=False),
    sa.Column('joy', sa.Integer(), nullable=True),
    sa.Column('sadness', sa.Integer(), nullable=True),
    sa.Column('anger', sa.Integer(), nullable=True),
    sa.Column('fear', sa.Integer(), nullable=True),
    sa.Column('disgust', sa.Integer(), nullable=True),
    sa.Column('anxiety', sa.Integer(), nullable=True),
    sa.Column('envy', sa.Integer(), nullable=True),
    sa.Column('bewilderment', sa.Integer(), nullable=True),
    sa.Column('boredom', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['diary_id'], ['diary.diary_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('emotion_id')
    )
    op.create_index(op.f('ix_emotions_emotion_id'), 'emotions', ['emotion_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_emotions_emotion_id'), table_name='emotions')
    op.drop_table('emotions')
    # ### end Alembic commands ###
