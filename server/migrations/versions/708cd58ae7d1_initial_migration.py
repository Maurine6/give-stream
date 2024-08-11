"""Initial migration

Revision ID: 708cd58ae7d1
Revises: 
Create Date: 2024-08-10 01:37:33.630436

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '708cd58ae7d1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('donations', schema=None) as batch_op:
        batch_op.drop_constraint('fk_donations_charity_id_charities', type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('fk_donations_charity_id_charities'), 'charities', ['charity_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('donations', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_donations_charity_id_charities'), type_='foreignkey')
        batch_op.create_foreign_key('fk_donations_charity_id_charities', 'charities', ['charity_id'], ['id'])

    # ### end Alembic commands ###
