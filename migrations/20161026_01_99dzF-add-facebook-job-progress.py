"""
add facebook job progress
"""

from yoyo import step

__depends__ = {'20161020_01_e4qVs-drop-facebook-groups'}

steps = [
    step("ALTER TABLE jobs RENAME progress to facebook_progress"),
    step("ALTER TABLE jobs ADD COLUMN "
         "youtube_progress SMALLINT NOT NULL DEFAULT 0")
]
