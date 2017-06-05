#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>
#Add pardusAccount and pardusLider objectClass to LDAP
# import needed modules

import ldap
import ldap.modlist as modlist

print("********************************")
print("*                              *")
print("*   Add pardusAccount and      *")
print("*   pardusLider objectClass    *")
print("*       to OpenLDAP            *")
print("*                              *")
print("********************************")

hostname = raw_input("ldap sunucu ip adresini giriniz(192.168.56.1): ")
search_base = raw_input("ldap search_base bilgisini giriniz(örn: dc=tuncay,dc=colak): ")
# hostname="192.168.56.102"
# search_base = "dc=tuncay,dc=colak"
base_dn = "cn=admin,"+str(search_base)
pwd = raw_input("ldap admin parolasını giriniz: ")
# pwd = "1"
ldap_obj = ldap.initialize(hostname)
ldap_obj.simple_bind_s(base_dn,pwd)
print ("ldap'a bağlantı kuruldu......")

search_scope = ldap.SCOPE_SUBTREE
searchAttribute = ["uid","objectClass","sn","cn","userPassword"]
search_filter = "(objectClass=inetOrgPerson)"
print (search_filter)
try:

    ldap_result = ldap_obj.search_s(search_base, search_scope, search_filter, searchAttribute)
    # ldap arama sonuçları user.ldif dosyasına yazılarak kullanıcıların yedeği alınıyor.
    f = open('user.ldif', 'w')
    s = str(ldap_result)
    f.write(s)
    f.close()

    attrs={}
    print ("arama sonucu sayısı: "+str(len(ldap_result)))
    print ("---------------------------------------------")
    new_user_list = []
    userNum = 1
    for user_list in ldap_result:
        print (str(userNum)+". kullanıcı için işlem yapılıyor.....")
        userdn = user_list[0]
        new_user_list.append(userdn)
        print ("kullancı listesi...--->> "+str(new_user_list))
        user_data = user_list[1]
        print (user_data)
        userNum = (userNum + 1)
        if not "pardusAccount" in user_data["objectClass"]:
            print (userdn)
            user_data["objectClass"].append("pardusAccount")
            user_data["objectClass"].append("pardusLider")
            ldap_obj.delete_s(userdn)
            print ('----->>> kullanıcı silindi.....!!!')
            user_data["userPassword"] = ['1']
            print (user_data)
            ldif = modlist.addModlist(user_data)
            ldap_obj.add_s(userdn,ldif)
            print ("----->>>>> kullanıcı eklendi....")
            print ("------------------------------------------------------------------------------")
        pass
except Exception as e:
    print (e)
    print ("ERROR --->>> işlem başarısız.....!!!")
ldap_obj.unbind_s()
