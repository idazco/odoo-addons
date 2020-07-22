{
    "name": "Tagged Notes",
    "version": "13.0.1.0.0",
    'description': "Tagged notes support",
    "author": "IDAZCO",
    "license": "AGPL-3",
    "depends": ["base", "project"],
    "application": True,
    "installable": True,
    "data": [
        "views/notes_tags_view.xml",
        'security/ir.model.access.csv',
    ]
}