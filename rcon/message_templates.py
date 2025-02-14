from rcon.models import enter_session, MessageTemplate
from rcon.types import (
    MessageTemplateCategory,
    MessageTemplateType,
    AllMessageTemplateTypes,
)
from sqlalchemy import select

# create
# retrieve
# update
# delete


def get_message_templates(
    category: MessageTemplateCategory,
) -> list[MessageTemplateType]:
    """Get all messgae templates for a specific category"""
    with enter_session() as session:
        stmt = select(MessageTemplate).where(
            MessageTemplate.category == category.upper()
        )
        res = session.scalars(stmt).all()
        return [msg.to_dict() for msg in res]


def get_message_template_categories() -> list[MessageTemplateCategory]:
    """Get all possible message type categories"""
    return [cat for cat in MessageTemplateCategory]


def get_message_template(id: int) -> MessageTemplate | None:
    """Return the message template for the specified record if it exists"""
    with enter_session() as session:
        stmt = select(MessageTemplate).where(MessageTemplate.id == id)
        res = session.scalars(stmt).one_or_none()
        return res


def get_all_message_templates() -> AllMessageTemplateTypes:
    """Get all message templates by category"""
    messages_by_cat: AllMessageTemplateTypes = {
        "AUTO_SETTINGS": [],
        "BROADCAST": [],
        "MESSAGE": [],
        "REASON": [],
        "WELCOME": [],
    }  # type: ignore

    with enter_session() as session:
        stmt = select(MessageTemplate)
        res = session.scalars(stmt).all()

        for msg in res:
            messages_by_cat[msg.category.value].append(msg.to_dict())

        return messages_by_cat


def _convert_category(
    category: str | MessageTemplateCategory,
) -> MessageTemplateCategory:
    if isinstance(category, str):
        category = category.upper()

    try:
        return MessageTemplateCategory[category]

    except KeyError:
        raise ValueError(
            f"Category must be one of {[msg.value for msg in MessageTemplateCategory]}"
        )


def add_message_template(
    title: str,
    content: str,
    category: str | MessageTemplateCategory,
    author: str = "CRCON",
) -> int:
    """Add a new message template and return the ID of the new record"""
    category = _convert_category(category=category)

    try:
        MessageTemplateCategory[category]
    except KeyError:
        raise ValueError(
            f"Category must be one of {[msg.value for msg in MessageTemplateCategory]}"
        )

    with enter_session() as session:
        template = MessageTemplate(
            title=title, content=content, category=category, updated_by=author
        )
        session.add(template)
        # Flush so we can get the new records ID
        session.flush()
        return template.id


def delete_message_template(id: int) -> bool:
    """Delete a specific message template"""
    with enter_session() as session:
        stmt = select(MessageTemplate).where(MessageTemplate.id == id)
        res = session.scalars(stmt).one_or_none()
        if res:
            session.delete(res)
            return True

    return False


def edit_message_template(
    id: int,
    title: str | None,
    content: str | None,
    category: str | MessageTemplateCategory | None,
    author: str = "CRCON",
) -> None:
    with enter_session() as session:
        stmt = select(MessageTemplate).where(MessageTemplate.id == id)
        res = session.scalars(stmt).one_or_none()
        if res:
            if title:
                res.title = title
            if content:
                res.content = content
            if category:
                res.category = _convert_category(category=category)

            res.updated_by = author
