import ldap
from django.conf import settings
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class LDAPServer(object):
    def __init__(self):
        self.server = settings.LDAP_SERVER_URI
        self.username = settings.LDAP_BIND_DN
        self.password = settings.LDAP_BIND_PASSWORD
        self.client = None

    def connection(self):
        try:
            self.client = ldap.initialize(self.server)
            self.client.simple_bind_s(self.username, self.password)
            return self.client
        except ldap.INVALID_CREDENTIALS:
            self.client.unbind()
            print('ldap dn 绑定失败')
            return None
        except ldap.SERVER_DOWN:
            print('ldap server 不可用')
            return None

    @staticmethod
    def search(client, username):
        result = client.search_s(settings.LDAP_BIND_SEARCH, ldap.SCOPE_SUBTREE, '(SamAccountName=%s)' % username)
        return result[0][0]


class LdapBackend:
    def authenticate(self, request, username=None, password=None, **kwargs):
        client = None
        if username is not None:
            client = LDAPServer().connection()
            if None:
                raise ldap.INVALID_CREDENTIALS
        try:
            user = LDAPServer.search(client, username)
            first_name = user.split(',')[0].split('=')[1]
            client.simple_bind_s(user, password)
            obj, created = UserModel.objects.get_or_create(username=username)
            if created:
                obj.set_password(password)
                obj.first_name = first_name
                obj.save()
            else:
                obj.set_password(password)
                obj.first_name = first_name
                obj.save()
            return obj
        except (Exception, ldap.INVALID_CREDENTIALS) as e:
            client.unbind()

    def get_user(self, user_id):
        try:
            user = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
        return user
