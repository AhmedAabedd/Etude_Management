# -*- coding: utf-8 -*-
{
    'name': 'Etude Management',
    'summary': 'Student and subject management for private tutoring',
    'description': """
                    Manage students, subjects, enrollments, attendance, and monthly payments
                    for private tutoring without classrooms.
    """,
    'author': 'Ahmed Abed',
    'website': '',
    'category': 'Education',
    'version': '1.0.0',
    'license': 'LGPL-3',

    'depends': [
        'base'
    ],

    'data': [
        'views/student_view.xml',
        'views/group_view.xml',
        'views/configuration_view.xml',
        'views/session_view.xml',
        'views/enrollment_view.xml',
        'views/menu.xml',
        'data/cron_data.xml',
    ],

    'application': True,
    'installable': True,
}
