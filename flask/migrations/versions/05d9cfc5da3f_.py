"""empty message

Revision ID: 05d9cfc5da3f
Revises: 098c3194b6d1
Create Date: 2016-08-05 16:24:25.444403

"""

# revision identifiers, used by Alembic.
revision = '05d9cfc5da3f'
down_revision = '098c3194b6d1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('face_image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phash', sa.String(length=128), nullable=True),
    sa.Column('identity', sa.Integer(), nullable=True),
    sa.Column('rep', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('face_image')
    ### end Alembic commands ###
