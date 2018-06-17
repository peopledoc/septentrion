BEGIN;

INSERT INTO "django_site" (
    "id",
    "domain",
    "name"
) VALUES (
    1,
    'example.com',
    'example.com'
);
ALTER SEQUENCE django_site_id_seq RESTART WITH 2;

INSERT INTO django_content_type(app_label, model) VALUES('auth', 'group');
INSERT INTO django_content_type(app_label, model) VALUES('auth', 'user');
INSERT INTO django_content_type(app_label, model) VALUES('auth', 'permission');
INSERT INTO django_content_type(app_label, model) VALUES('contenttypes', 'contenttype');
INSERT INTO django_content_type(app_label, model) VALUES('sites', 'site');

INSERT INTO auth_permission(codename, name, content_type_id) VALUES('add_permission', 'Can add permission', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'permission'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('change_permission', 'Can change permission', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'permission'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('delete_permission', 'Can delete permission', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'permission'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('add_group', 'Can add group', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'group'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('change_group', 'Can change group', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'group'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('delete_group', 'Can delete group', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'group'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('add_user', 'Can add user', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'user'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('change_user', 'Can change user', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'user'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('delete_user', 'Can delete user', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'user'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('add_contenttype', 'Can add content type', (SELECT id FROM django_content_type WHERE app_label = 'contenttypes' AND model = 'contenttype'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('change_contenttype', 'Can change content type', (SELECT id FROM django_content_type WHERE app_label = 'contenttypes' AND model = 'contenttype'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('delete_contenttype', 'Can delete content type', (SELECT id FROM django_content_type WHERE app_label = 'contenttypes' AND model = 'contenttype'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('add_site', 'Can add site', (SELECT id FROM django_content_type WHERE app_label = 'sites' AND model = 'site'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('change_site', 'Can change site', (SELECT id FROM django_content_type WHERE app_label = 'sites' AND model = 'site'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('delete_site', 'Can delete site', (SELECT id FROM django_content_type WHERE app_label = 'sites' AND model = 'site'));

-- possible with pg >= 9.5:
-- INSERT INTO sql_version(version_num) VALUES ('0.1') ON CONFLICT (version_num) DO NOTHING;
-- pg 9.4:
INSERT INTO sql_version(version_num) SELECT '0.1' WHERE NOT EXISTS (SELECT 1 FROM sql_version WHERE version_num = '0.1');

COMMIT;
