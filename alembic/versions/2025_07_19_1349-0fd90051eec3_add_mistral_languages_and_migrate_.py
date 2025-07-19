"""Add Mistral Languages and Language Channels and migrate old channels

Revision ID: add_mistral_languages_and_migrate_channels
Revises: add_mistral_translator
Create Date: 2025-01-19 16:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
mistr_lang_and_migr_chan


# revision identifiers, used by Alembic.
revision = "mistr_lang_and_migr_chan"
down_revision = "add_mistral_translator"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем таблицу mistral_languages
    op.create_table(
        "mistral_languages",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("api_key", sa.String(), nullable=False),
        sa.Column("agent_id", sa.String(), nullable=False),
        sa.Column("status", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Создаем таблицу language_channels
    op.create_table(
        "language_channels",
        sa.Column("language_id", sa.Integer(), nullable=False),
        sa.Column("channel_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(["language_id"], ["mistral_languages.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Заполняем начальные данные языков
    languages_data = [
        ("Польский", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250718:polskii:3be9155a"),
        ("Чешский", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250717:cheshskii:a70b740a"),
        ("Словацкий", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250718:slovakskii:d2c3db0b"),
        ("Итальянский", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250718:untitled-agent:7edb9121"),
        ("Французский", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250718:frantsuzskii:ccf0ef52"),
        ("Английский", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250718:angliiskii:f1baade1"),
        ("Испанский", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250718:untitled-agent:4f70273c"),
        ("Немецкий", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250718:untitled-agent:d7dfc12a"),
        ("Голландский", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250718:untitled-agent:dfc91869"),
        ("Греческий", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250718:grecheskii:d43a98ae"),
        ("Венгерский", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250718:untitled-agent:05e9543a"),
        ("Румынский", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250718:rumynskii:4d53625e"),
        ("Болгарский", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250718:bolgarskii:48b6cda9"),
        ("Сербский", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250718:serbskii:c5cac31c"),
        ("Финский", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250718:untitled-agent:13d5a00c"),
        ("Турецкий", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250718:turetskii:f75072e6"),
        ("Иврит", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250718:untitled-agent:c9c25a93"),
        ("Арабский", "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5", "ag:9885ec37:20250718:arabskii:02db6b42"),
    ]

    mistral_languages_table = sa.table(
        "mistral_languages",
        sa.column("name", sa.String),
        sa.column("api_key", sa.String),
        sa.column("agent_id", sa.String),
        sa.column("status", sa.Boolean),
    )
    
    connection = op.get_bind()
    for name, api_key, agent_id in languages_data:
        connection.execute(
            mistral_languages_table.insert().values(
                name=name,
                api_key=api_key,
                agent_id=agent_id,
                status=True
            )
        )

    # Миграция старых каналов к новой системе
    language_mapping = {
        'RU': 'Русский',
        'EN': 'Английский', 
        'EN-US': 'Английский',
        'EN-GB': 'Английский',
        'DE': 'Немецкий',
        'FR': 'Французский',
        'ES': 'Испанский',
        'IT': 'Итальянский',
        'PL': 'Польский',
        'CS': 'Чешский',
        'SK': 'Словацкий',
        'NL': 'Голландский',
        'EL': 'Греческий',
        'HU': 'Венгерский',
        'RO': 'Румынский',
        'BG': 'Болгарский',
        'FI': 'Финский',
        'TR': 'Турецкий',
    }

    inspector = sa.inspect(connection)
    channels_columns = [col['name'] for col in inspector.get_columns('channels')]

    if 'language' in channels_columns:
        channels_result = connection.execute(
            sa.text("SELECT channel_id, language FROM channels WHERE language IS NOT NULL")
        ).fetchall()

        languages_result = connection.execute(
            sa.text("SELECT id, name FROM mistral_languages")
        ).fetchall()

        languages_dict = {lang[1]: lang[0] for lang in languages_result}

        if 'Русский' not in languages_dict:
            result = connection.execute(
                sa.text("""
                    INSERT INTO mistral_languages (name, api_key, agent_id, status)
                    VALUES ('Русский', 'FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5', 'ag:default:russian', true)
                    RETURNING id
                """)
            )
            russian_id = result.fetchone()[0]
            languages_dict['Русский'] = russian_id

        for channel_id, old_language in channels_result:
            new_language_name = language_mapping.get(old_language, 'Русский')
            language_id = languages_dict.get(new_language_name)
            if language_id:
                existing = connection.execute(
                    sa.text("""
                        SELECT id FROM language_channels WHERE language_id = :lang_id AND channel_id = :chan_id
                    """),
                    {"lang_id": language_id, "chan_id": channel_id}
                ).fetchone()
                if not existing:
                    connection.execute(
                        sa.text("""
                            INSERT INTO language_channels (language_id, channel_id) VALUES (:lang_id, :chan_id)
                        """),
                        {"lang_id": language_id, "chan_id": channel_id}
                    )

        op.drop_column('channels', 'language')
        connection.commit()


def downgrade() -> None:
    # Восстанавливаем поле language
    op.add_column('channels', sa.Column('language', sa.String(), nullable=True))

    reverse_mapping = {
        'Русский': 'RU',
        'Английский': 'EN-US',
        'Немецкий': 'DE', 
        'Французский': 'FR',
        'Испанский': 'ES',
        'Итальянский': 'IT',
        'Польский': 'PL',
        'Чешский': 'CS',
        'Словацкий': 'SK',
        'Голландский': 'NL',
        'Греческий': 'EL',
        'Венгерский': 'HU',
        'Румынский': 'RO',
        'Болгарский': 'BG',
        'Финский': 'FI',
        'Турецкий': 'TR',
    }

    connection = op.get_bind()
    result = connection.execute(
        sa.text("""
            SELECT lc.channel_id, ml.name FROM language_channels lc
            JOIN mistral_languages ml ON lc.language_id = ml.id
        """)
    ).fetchall()

    for channel_id, language_name in result:
        old_language_code = reverse_mapping.get(language_name, 'RU')
        connection.execute(
            sa.text("UPDATE channels SET language = :lang WHERE channel_id = :chan_id"),
            {"lang": old_language_code, "chan_id": channel_id}
        )

    connection.commit()
