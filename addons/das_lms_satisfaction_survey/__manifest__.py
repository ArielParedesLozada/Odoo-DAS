{
    "name": "DAS LMS Satisfaction Survey",
    "version": "1.0",
    "category": "Website/eLearning",
    "author": "DAS",
    "license": "LGPL-3",
    "depends": ["base", "survey", "website_slides", "das_lms", "das_lms_certificates"],
    "data": [
        "security/ir.model.access.csv",
        "views/satisfaction_survey_views.xml",
        "views/survey_result_inherit.xml",
        "data/satisfaction_survey_data.xml",
    ],
    "installable": True,
}
