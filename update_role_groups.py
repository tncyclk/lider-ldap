#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>

from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_ADD, ALL_ATTRIBUTES

""" 
Uygulamayı çalıştırmadan önce sudo apt install python3-ldap3 paketi kurulmalıdır. Daha sonra python3 update_role_groups.py komutu ile betik çalıştırılır.
Bu betik ou=Roles grubu altında sudoRole  olarak tanımlanan role'leri buluyor. Daha sonra bulunan role ait sudoPardusBirimId ler bulunur. 
Ahenk register olduğunda pardusBirimId attribute de gelmelidir. Role grubunda tanımlanan sudoPardusBirimId ye sahip ahenklerde tanımlanmış pardusBirimId ler bulunur. Bulunan bu birim id lere sahip 
ahenkler role grubuna sudoHost olarak eklenir. Burada dikkat edilmesi gereken durum; role tanımlanacak sudoHost değerinin ahenk makinesinin hostname ile aynı olması gerektiğidir.
Bu hostname değeri ahenklerdeki uid ile aynı olduğu için uid değeri host olarak döndürülmektedir. Örn;

ou=Roles grubu altında TT role'lerini bul (TT-Ankara) --->> Bu role ait sudoPardusBirimId bul (sudoPardusBirimId: 0001) --->>> Bulunan sudoPardusBirimId (0001) ye sahip ahenkler bulunur. yani pardusBirimId değeri bulunur.
(pardusBirimId=0001) pardusBirimId li çok fazla ahenkte tanımlanmış olacaktır. --->> Bulunan pardusBirimId=0001 değerine sahip ahenkin uid değeri alınır. (uid = ab1011-1001)--->>
Uid değeri TT-Ankara grubuna sudoHost olarak eklenir.

NOT:
        self.server = 'ldap_server'
        self.base_dn = 'ldap_base_dn'
        self.user_dn = 'cn=admin,'+str(self.base_dn)
        self.user_password = 'ldap_admin_pwd'
        
    değerlerini deiştirmeyi unutmayın..!!

"""

class RoleGroup(object):
    def __init__(self):
        self.server = 'ldap_server'
        self.base_dn = 'ldap_base_dn'
        self.user_dn = 'cn=admin,'+str(self.base_dn)
        self.user_password = 'ldap_admin_pwd'
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


    # get_ldap_roles metodu sudoRole objectClass ına sahip role'leri bulmaktadır. Bulunan bu rollere ait sudoPardusBirimId attribute'leri bulunarak get_agent_uid(birim_id[0]) metoduna gönderilir.

    def get_ldap_roles(self):
        total_entries = 0
        self.ldap_bind()

        self.l_obj.search(search_base=self.base_dn,
               search_filter='(objectClass=sudoRole)',
               search_scope=SUBTREE,
               attributes=['sudoPardusBirimId', 'entryDN'])
        total_entries += len(self.l_obj.response)

        for entry in self.l_obj.response:
            print("-----------------------------------------------------------------------------------------------")
            birim_id = entry['attributes']['sudoPardusBirimId']
            print("Birim Id--->>> "+str(birim_id))
            role_dn = entry['attributes']['entryDN']

            agents = self.get_agent_uid(birim_id[0])

            # bu for döngüsünde host role eklenecek sudoHost değeridir. Bu değer ahenk makinesinin hostname'i ile aynı olmak durumundadır. ahenklerde tanımlanan uid değerleri hostname
            # olduğu için host değişkeni uid attribute'nden alınmaktadır.

            for host in agents:
                self.ldap_modify(host, role_dn)


    #Bu metotda roles grubunda bulunan sudoPardusBirimId değerleri ile aynı olan pardusBirimId değerleri bulunur. pardusBirimId attribute'lerinin ahenklere tanımlanmış olması gerekir.
    # Bu birim id ler birden fazla ahenklere tanımlanmış olduğu için bir list döndürülmektedir.

    def get_agent_uid(self, birim_id):
        agent_uid_list = []
        self.l_obj.search(search_base=self.base_dn,
                          search_filter='(pardusBirimId={})'.format(birim_id),
                          search_scope=SUBTREE,
                          attributes=[ALL_ATTRIBUTES])

        for entry in self.l_obj.response:
            # print(entry['attributes']['sudoUser'])
            for uid in entry['attributes']['uid']:
                agent_uid_list.append(uid)

        return agent_uid_list



    # Bu metotda bulunan ahenk/ler TT ofis kullanıcısının üyesi olduğu role grubuna sudoHost olarak eklenir.
    def ldap_modify(self, host, role_dn):
        self.l_obj.modify(role_dn,
                 {'sudoHost': [(MODIFY_ADD, [str(host)])]})
        print(str(host)+" makinesi "+str(role_dn)+" yetkilendirme grubuna sudoHost olarak eklendi\n")


if __name__ == '__main__':
    app = RoleGroup()
    app.get_ldap_roles()
    app.ldap_unbind()