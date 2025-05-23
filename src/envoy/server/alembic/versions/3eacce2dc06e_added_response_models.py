"""added_response_models

Revision ID: 3eacce2dc06e
Revises: 5c4cb6749db0
Create Date: 2025-03-11 17:22:41.153313

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3eacce2dc06e"
down_revision = "5c4cb6749db0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "dynamic_operating_envelope_response",
        sa.Column("dynamic_operating_envelope_response_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("dynamic_operating_envelope_id", sa.BigInteger(), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("created_time", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("response_type", sa.INTEGER(), nullable=True),
        sa.ForeignKeyConstraint(
            ["dynamic_operating_envelope_id"],
            ["dynamic_operating_envelope.dynamic_operating_envelope_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["site_id"], ["site.site_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("dynamic_operating_envelope_response_id"),
    )
    op.create_index(
        "ix_dynamic_operating_envelope_response_site_id_created_time",
        "dynamic_operating_envelope_response",
        ["site_id", "created_time"],
        unique=False,
    )
    op.create_table(
        "tariff_generated_rate_response",
        sa.Column("tariff_generated_rate_response_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tariff_generated_rate_id", sa.BigInteger(), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("created_time", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("response_type", sa.INTEGER(), nullable=True),
        sa.Column("pricing_reading_type", sa.SMALLINT(), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["site.site_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["tariff_generated_rate_id"], ["tariff_generated_rate.tariff_generated_rate_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("tariff_generated_rate_response_id"),
    )
    op.create_index(
        "ix_tariff_generated_rate_response_site_id_created_time",
        "tariff_generated_rate_response",
        ["site_id", "created_time"],
        unique=False,
    )
    op.drop_index("aggregator_id", table_name="subscription")
    op.create_index(
        "ix_subscription_aggregator_id_resource_type", "subscription", ["aggregator_id", "resource_type"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_subscription_aggregator_id_resource_type", table_name="subscription")
    op.create_index("aggregator_id", "subscription", ["resource_type"], unique=False)
    op.drop_index("ix_tariff_generated_rate_response_site_id_created_time", table_name="tariff_generated_rate_response")
    op.drop_table("tariff_generated_rate_response")
    op.drop_index(
        "ix_dynamic_operating_envelope_response_site_id_created_time", table_name="dynamic_operating_envelope_response"
    )
    op.drop_table("dynamic_operating_envelope_response")
    # ### end Alembic commands ###
