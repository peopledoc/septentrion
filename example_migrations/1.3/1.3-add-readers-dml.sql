BEGIN;

    INSERT INTO django_content_type(app_label, model) VALUES('north_app', 'reader');
    INSERT INTO auth_permission(codename, name, content_type_id) VALUES('add_reader', 'Can add reader', (SELECT id FROM django_content_type WHERE app_label = 'north_app' AND model = 'reader'));
    INSERT INTO auth_permission(codename, name, content_type_id) VALUES('change_reader', 'Can change reader', (SELECT id FROM django_content_type WHERE app_label = 'north_app' AND model = 'reader'));
    INSERT INTO auth_permission(codename, name, content_type_id) VALUES('delete_reader', 'Can delete reader', (SELECT id FROM django_content_type WHERE app_label = 'north_app' AND model = 'reader'));

COMMIT;
