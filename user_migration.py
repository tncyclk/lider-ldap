#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>

import os
import ezodf
from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_ADD, ALL_ATTRIBUTES
from random import randint

# user import to OpenLDAP tool

class Migration(object):
    """docstring for RosterItem"""
    def __init__(self):
        super(Migration, self).__init__()
        self.base_dn = "dc=liderahenk,dc=org"
        self.ldap_admin_dn = "cn=admin,"+str(self.base_dn)
        self.pwd = "1"
        self.ldap_server = "192.168.56.1"
        self.l_obj = None

        self.user_list_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.ods')

    def ldap_bind(self):
        # define the server
        s = Server(self.ldap_server, get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema
        # define the connection
        self.l_obj = Connection(s, user=self.ldap_admin_dn, password=self.pwd, auto_bind=True)
        # perform the Bind operation
        if not self.l_obj.bind():
            print('error in bind', self.l_obj.result)
        else:
            print("\nSusccessful connect to OpenLDAP\n")

    def ldap_unbind(self):
        self.l_obj.unbind()
        print("\nunbind to OpenLDAP\n")

    def ldap_search_by_dn(self, dn):
        self.l_obj.search(search_base=self.base_dn,
                          search_filter='(entryDN={})'.format(dn),
                          search_scope=SUBTREE,
                          attributes=["entryDN"])
        if self.l_obj.response:
            print("*** {0} zaten var".format(dn))
            return True
        else:
            print("-->> {0} bulunamadı".format(dn))
            return False

    def ldap_search_by_uid_number(self, uid_number):
        self.l_obj.search(search_base=self.base_dn,
                          search_filter='(uidNumber={})'.format(uid_number),
                          search_scope=SUBTREE,
                          attributes=["entryDN"])
        if self.l_obj.response:
            return True
        else:
            return False

    def import_user(self):
        self.ldap_bind()
        ezodf.config.set_table_expand_strategy('all')
        doc = ezodf.opendoc(self.user_list_path)
        sheet = doc.sheets[0]

        print("Spreadsheet contains %d sheet(s)." % len(doc.sheets))
        for sheet in doc.sheets:
            print("-" * 40)
            print("   Sheet name : '%s'" % sheet.name)
            print("Size of Sheet : (rows=%d, cols=%d)" % (sheet.nrows(), sheet.ncols()))

        user_size = sheet.nrows() + 1
        for i in range(2, user_size):
            uid_number = randint(6000, 50000)
            while True:
                if self.ldap_search_by_uid_number(uid_number):
                   uid_number = randint(6000, 50000)
                else:
                    break

            user_data = {
                'uid': sheet['A{}'.format(i)].value,
                'cn': sheet['B{}'.format(i)].value,
                'sn': sheet['C{}'.format(i)].value,
                'ou': sheet['D{}'.format(i)].value,
                # 'uidNumber': sheet['D{}'.format(i)].value,
                'uidNumber': uid_number,
                # 'gidNumber': sheet['E{}'.format(i)].value,
                'gidNumber': 7500,
                'userPassword': sheet['A{}'.format(i)].value,
                'mail': sheet['E{}'.format(i)].value
            }
            uid = str(user_data['uid'])
            ou = user_data['ou']
            ou_parser = ou.split(",")
            ou = "ou={0},ou=Users,{1}".format(ou_parser[0], self.base_dn)
            if self.ldap_search_by_dn(ou) is False:
                self.add_ou(ou)
            ou_size = len(ou_parser)-1
            for x in range(ou_size):
                x = x+1
                ou = "ou={0},{1}".format(ou_parser[x], ou)
                if self.ldap_search_by_dn(ou) is False:
                    self.add_ou(ou)

            user_dn = "uid={0},{1}".format(uid, ou)
            if self.ldap_search_by_dn(user_dn) is False:
                self.add_user(user_data, user_dn)

        self.ldap_unbind()

    def add_ou(self, ou):
        try:
            ou_parser = ou.split(",")
            ou_name = ou_parser[0].replace("ou=", "")
            self.l_obj.add(ou,
                  attributes={'objectClass': ['organizationalUnit', 'top', 'pardusLider'],
                              'ou': ou_name})
            print("{0} eklendi".format(ou))
        except Exception as e:
            print(e)

    def add_user(self, user_data, user_dn):
        uid = user_dn.split(",")[0].replace("uid=", "")
        try:
            self.l_obj.add(user_dn,
                  attributes={'objectClass': ['inetOrgPerson', 'posixAccount', 'top', 'organizationalPerson', 'pardusAccount', 'pardusLider', 'person'],
                              'sn': user_data['sn'],
                              'cn': user_data['cn'],
                              'gidNumber': user_data['gidNumber'],
                              'uidNumber': user_data['uidNumber'],
                              'userPassword': user_data['userPassword'],
                              'homeDirectory': '/home/'+uid,
                              'loginShell': '/bin/bash',
                              'mail': user_data['mail']})

            print("--->> {0} kullanıcı eklendi...".format(uid))
        except Exception as e:
            print(e)


if __name__ == '__main__':
    app = Migration()
    app.import_user()

