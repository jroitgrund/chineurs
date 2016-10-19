"""
Make timestamp include tz info
"""

from yoyo import step

__depends__ = {'20161019_02_TYxnu-make-google-credentials-bytea'}

steps = [
    step("ALTER TABLE playlist_inserts ALTER COLUMN datetime TYPE timestamptz "
         "USING datetime::timestamptz")
]
