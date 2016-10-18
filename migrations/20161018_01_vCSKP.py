"""
Initial schema
"""

from yoyo import step

__depends__ = {}

steps = [
    step("CREATE TABLE jobs "
         "(id BIGSERIAL PRIMARY KEY, progress SMALLINT NOT NULL DEFAULT 0)"),
    step("CREATE TABLE users "
         "(id BIGSERIAL PRIMARY KEY, email TEXT UNIQUE NOT NULL, "
         "fb_access_token TEXT, google_credentials TEXT)"),
    step("CREATE TABLE playlist_inserts "
         "(playlist_id TEXT NOT NULL, group_id TEXT NOT NULL, "
         "PRIMARY KEY(playlist_id, group_id))")
]
