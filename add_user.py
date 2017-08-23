#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>
# import needed modules
# add user to ldap for test
import ldap
import ldap.modlist as modlist

print("********************************")
print("*                              *")
print("*       Add user to            *")
print("*        OpenLDAP              *")
print("*                              *")
print("********************************")

# Open a connection with ldap server
hostname = raw_input("ldap sunucu ip adresini giriniz: ")
search_base = raw_input("ldap search_base bilgisini giriniz(örn: dc=tuncay,dc=colak): ")
pwd = raw_input("ldap admin parolası: ")
# hostname="192.168.56.102"
# search_base = "dc=tuncay,dc=colak"
base_dn = "cn=admin,"+str(search_base)
ldap_obj = ldap.open(hostname)
ldap_obj.simple_bind_s(base_dn, pwd)

# add test group to ldap
print ("------------------------------------------------------------")
groupName = raw_input("eklemek istedğiniz grup adını giriniz: ")
dnGroup = "ou="+str(groupName)+","+str(search_base)
print ("eklenecek grup---->>> "+str(dnGroup))
attrs = {}
attrs['objectclass'] = ['top', 'organizationalUnit']
attrs['ou'] = groupName
attrs['description'] = 'test grup'
print('---->  grup  basariyla olusturuldu..! <----')
ldif = modlist.addModlist(attrs)
ldap_obj.add_s(dnGroup,ldif)
print("-------------------------------------------------------------")

# add user to ldap
userNum = raw_input("eklemek istediğiniz kullanıcı sayısını giriniz: ")
print("-------------------------------------------------------------")
for user in range(1,int(userNum)):

    dn="uid=user"+str(user)+","+str(dnGroup)
    uid_num = (4999 + user)
    # uidNumber ve gidNumber değerleri 5000'den başlatılıyor.
    print (str(uid_num))
    attrs = {}
    attrs['objectclass'] = ['top', 'posixAccount', 'shadowAccount', 'organizationalPerson', 'inetOrgPerson', 'pardusAccount', 'pardusLider', 'person']
    # objectClass can be added object class'lar arttırılabilir.
    attrs['cn'] = 'user'+str(user)
    attrs['sn'] = 'user'+str(user)
    attrs['uid'] = 'user'+str(user)
    attrs['uidNumber'] = str(uid_num)
    attrs['gidNumber'] = str(uid_num)
    attrs['homeDirectory'] = '/home/user'+str(user)
    attrs['loginShell'] = '/bin/bash'
    attrs['description'] = 'test kulllanıcısı ekleme'
    attrs['userPassword'] = '123'

    # Convert our dict to nice syntax for the add-function using modlist-module
    ldif = modlist.addModlist(attrs)
    print (ldif)

    # Do the actual synchronous add-operation to the ldapserver
    ldap_obj.add_s(dn,ldif)
    print (str(dn)+" kullanıcısı eklendi...!!")
    print ("-------------------------------------------------------------------------------")

# disconnect ldap server
ldap_obj.unbind_s()
