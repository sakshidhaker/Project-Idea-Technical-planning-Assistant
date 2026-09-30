"""Admin dashboard data (users, chats, latest messages)."""
from backend import database


def overview(search=""):
    return {"stats": database.stats(), "users": database.list_users(search),
            "recent": database.recent_messages(25)}


def remove_user(user_id, admin_id):
    if user_id != admin_id:               # admin cannot delete himself
        database.delete_user(user_id)
