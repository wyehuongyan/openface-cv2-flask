"""empty message

Revision ID: 2f4d64a63cc0
Revises: 05d9cfc5da3f
Create Date: 2016-08-05 16:44:20.122021

"""

# revision identifiers, used by Alembic.
revision = '2f4d64a63cc0'
down_revision = '05d9cfc5da3f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('face_image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phash', sa.String(length=128), nullable=True),
    sa.Column('identity', sa.Integer(), nullable=True),
    sa.Column('rep', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('face_image')
    ### end Alembic commands ###
