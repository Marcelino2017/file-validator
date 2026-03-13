from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "enterprises",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("nit", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_enterprises_nit",
        "enterprises",
        ["nit"],
        unique=True,
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("first_name", sa.String(length=80), nullable=False),
        sa.Column("last_name", sa.String(length=80), nullable=False),
        sa.Column("cedula", sa.String(length=20), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "enterprise_id",
            sa.Integer(),
            sa.ForeignKey("enterprises.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_users_cedula",
        "users",
        ["cedula"],
        unique=True,
    )
    op.create_index(
        "ix_users_enterprise_id",
        "users",
        ["enterprise_id"],
    )

    op.create_table(
        "pdf_documents",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=60), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "enterprise_id",
            sa.Integer(),
            sa.ForeignKey("enterprises.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_pdf_documents_user_id",
        "pdf_documents",
        ["user_id"],
    )
    op.create_index(
        "ix_pdf_documents_enterprise_id",
        "pdf_documents",
        ["enterprise_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_pdf_documents_enterprise_id", table_name="pdf_documents")
    op.drop_index("ix_pdf_documents_user_id", table_name="pdf_documents")
    op.drop_table("pdf_documents")

    op.drop_index("ix_users_enterprise_id", table_name="users")
    op.drop_index("ix_users_cedula", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_enterprises_nit", table_name="enterprises")
    op.drop_table("enterprises")

