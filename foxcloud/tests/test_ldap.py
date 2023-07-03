from foxcloud import client

params = {
    'dn': 'cn=admin,dc=ldap,dc=foxcloud,dc=vn',
    'ldap_endpoint': 'ldap://172.16.1.56',
    'password': 'Cas@2020'
}
cs = client.Client('1', engine='console', services='ldap',  **params)
# result = cs.ldap.test()
# print(cs.ldap.change_password('cn=tiendc2,ou=Users,dc=ldap,dc=foxcloud,dc=vn', 'khanhct1234', 'khanhct12344'))
# # print(cs.ldap.delete_user('cn=khanhct,ou=Users,dc=ldap,dc=foxcloud,dc=vn'))
print(cs.ldap.create_user(dn='ou=Users,dc=ldap,dc=foxcloud,dc=vn',
                          username='tiendc3', password='Cas@2020'))
print(cs.ldap.add_to_group(user_dn='cn=tiendc3,ou=Users,dc=ldap,dc=foxcloud,dc=vn',
                           group_dn='cn=OSuser,ou=Groups,dc=ldap,dc=foxcloud,dc=vn'))
# cs.ldap.unbind()
