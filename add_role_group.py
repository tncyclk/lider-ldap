#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>

from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_ADD, ALL_ATTRIBUTES

""" 
Uygulamayı çalıştırmadan önce sudo apt install python3-ldap3 paketi kurulmalıdır. Daha sonra python3 add_role_group.py komutu ile betik çalıştırılır.
Bu betik ou=Roles grubu altında sudoRole  olarak tanımlanan role'leri buluyor. Daha sonra bulunan role ait teknik ofis kullanıcıları bulunur. 
Ahenk'i register yapan kullanıcı ldap ta register olan ahenk in ownerı olarak tanımlanacak. Bulunan teknik ofis kullanıcısının ya da kullanıcılarının owner ı olduğu ahenkler bulunarak 
role grubuna sudoHost olarak eklemektedir.

ou=Roles grubu altında TT role'lerini bul (TT-Ankara) --->> Bu role ait kullanıcılarını bul (sudoUser: user12) --->>> Bulunan tt (user12) kullanıcısının owner'ı olduğu ahenk'i bul ve bu ahenkin uid değerini döndür
(uid: ahenk12) --->> Bulunan ahenk sudoUser: user12 nin üyesi olduğu TT-Ankara grubuna (suduHost: ahenk12) olarak eklenir.

"""

class RoleGroup(object):
    def __init__(self):
        self.server = '192.168.56.111'
        self.base_dn = 'dc=liderahenk,dc=org'
        self.user_dn = 'cn=admin,'+str(self.base_dn)
        self.user_password = '1'
        self.l_obj = None

    def ldap_bind(self):
        # define the server
        s = Server(self.server, get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema
        # define the connection
        self.l_obj = Connection(s, user=self.user_dn, password=self.user_password)
        # perform the Bind operation
        if not self.l_obj.bind():
            print('error in bind', self.l_obj.result)
        else:
            print("\nSusccessful connect to OpenLDAP\n")

    def ldap_unbind(self):
        self.l_obj.unbind()
        print("unbind to OpenLDAP")


    # get_ldap_roles metodu sudoRole objectClass ına sahip role'leri bulmaktadır. Bulunan role'lerin dn leri get_sudo_user(self, role_dn): metoduna
    #  gönderilerek bu role ait teknik ofis kullanıcıları bulunuyor.

    def get_ldap_roles(self):
        total_entries = 0
        self.ldap_bind()

        self.l_obj.search(search_base=self.base_dn,
               search_filter='(objectClass=sudoRole)',
               search_scope=SUBTREE,
               attributes=['sudoUser', 'entryDN'])
        total_entries += len(self.l_obj.response)

        for entry in self.l_obj.response:
            print("-----------------------------------------------------------------------------------------------")
            print("Role--->>> "+entry['attributes']['entryDN'])
            role_dn = entry['attributes']['entryDN']
            self.get_sudo_user(role_dn)


    # Bu metoda gönderilen role_dn parametresi get_ldap_roles metodunda bulunan role grubuna (ÖRN: TT-Ankara) ait teknik ofis kullanısılarını bulmaktadır.
    # Bulunan kullanıcıların owner'ı oladuğu makineleri bulmak için ise get_agent(user) user parametresi göderilerek ahenkler döndürülüyor.

    def get_sudo_user(self, role_dn):
        self.l_obj.search(search_base=self.base_dn,
                          search_filter='(entryDN={})'.format(role_dn),
                          search_scope=SUBTREE,
                          attributes=['sudoUser'])

        for entry in self.l_obj.response:
            # print(entry['attributes']['sudoUser'])
            for user in entry['attributes']['sudoUser']:
                agents = self.get_agent(user)
                print(user + " --->> kullanıcısının owner'ı olduğu ahenk/ler: " + str(agents) + "\n")
                for agent_uid in agents:
                    self.ldap_modify(agent_uid, role_dn)

    def get_agent(self, uid):
        agent_list = []
        self.l_obj.search(search_base=self.base_dn,
                          search_filter='(uid={})'.format(uid),
                          search_scope=SUBTREE,
                          attributes=['entryDN'])

        for entry in self.l_obj.response:
            # print(entry['attributes'])
            user_dn = entry['attributes']['entryDN']
            self.l_obj.search(search_base=self.base_dn,
                             search_filter='(owner={})'.format(user_dn),
                             search_scope=SUBTREE,
                             attributes=[ALL_ATTRIBUTES])

            for entry in self.l_obj.response:
                # print(entry['attributes']['uid'])
                agent_dn = entry['attributes']['uid']
                agent_list.append(str(agent_dn))
        return agent_list

    # Bu metotda bulunan ahenk/ler TT ofis kullanıcısının üyesi olduğu role grubuna sudoHost olarak eklenir.
    def ldap_modify(self, agent_uid, role_dn):
        agent_uid = agent_uid.replace("['", "")
        agent_uid = agent_uid.replace("']", "")
        self.l_obj.modify(role_dn,
                 {'sudoHost': [(MODIFY_ADD, [str(agent_uid)])]})
        print(str(agent_uid)+" makinesi sudoHost olarak eklendi\n")

    def ldap_del(self):
        pass

if __name__ == '__main__':
    app = RoleGroup()
    app.get_ldap_roles()