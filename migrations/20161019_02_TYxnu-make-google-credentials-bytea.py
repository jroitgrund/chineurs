"""
Make google credentials bytea
"""

from yoyo import step

__depends__ = {'20161019_01_oENaE-add-date-to-playlist-inserts'}

steps = [
    step("ALTER TABLE users ALTER COLUMN google_credentials TYPE bytea "
         "USING google_credentials::bytea")
]
