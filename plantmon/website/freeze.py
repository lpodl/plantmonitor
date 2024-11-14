"""
using frozen flask to generate static website
"""
from flask_frozen import Freezer
from app import app


app.config.update({
    'FREEZER_RELATIVE_URLS': True,
    'FREEZER_DESTINATION': 'build',
    'FREEZER_IGNORE_MIMETYPE_WARNINGS': True
})

freezer = Freezer(app)

if __name__ == '__main__':
    freezer.freeze()