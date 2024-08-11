"""deletion

Revision ID: 54a8fd753fef
Revises: 9ea7c2ee371b
Create Date: 2024-08-11 20:26:33.141100

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '54a8fd753fef'
down_revision = '9ea7c2ee371b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.drop_column('checkout_request_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('checkout_request_id', sa.VARCHAR(length=255), nullable=False))

    # ### end Alembic commands ###
