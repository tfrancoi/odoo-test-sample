# -*- coding: utf-8 -*-
{
    'name': "Shift Management",

    'summary': """
        Volonteer Timetable Management""",

    'description': """

    """,

    'author': "Thibault Francois",
    'website': "",

    'category': 'Cooperative management',
    'version': '0.1',

    'depends': ['base', 'mail'],

    'data': [
        "data/stage.xml",
        "data/system_parameter.xml",
        "data/cron.xml",
        "security/group.xml",
        "security/ir.model.access.csv",
        "views/task_template.xml",
        "views/task.xml",
        "views/planning.xml",
        "views/cooperative_status.xml",
        "views/exempt_reason.xml",
        "wizard/instanciate_planning.xml",
        "wizard/batch_template.xml",
        "wizard/assign_super_coop.xml",
        "wizard/subscribe.xml",
        "wizard/extension.xml",
        "wizard/holiday.xml",
    ],
    
    'demo': [
        "demo/demo.xml",
    ],
}
