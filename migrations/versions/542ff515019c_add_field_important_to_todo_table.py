"""add field important to todo table

Revision ID: 542ff515019c
Revises: 
Create Date: 2022-08-12 22:04:32.929441

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '542ff515019c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('todos', sa.Column('important', sa.Boolean(), nullable=True))
    op.alter_column('todos', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('todos', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('todos', 'important')
    # ### end Alembic commands ###
