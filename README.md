# Liderahenk OpenLDAP Kullanıcı Entegrasyonu
* users dosyasında bulunan kullanıcıların OpenLDAP'a aktarılması amaçlanmaktadır. users dosyası,


        uid	        cn	sn	ou	                                        mail
        user1	user1	USER1	Bilgi İşlem Daire,Sistem Şube,Lider sistem	user1@liderahenk.org


şeklinde düzenlenmelidir. Burada yer alan ou parametresi kullanıcının **ou=Users** altında bulunacağı hiyerarşiyi ifade etmektedir. 
ou parametresi örnekte gösterildiği şekliyle "," ile hiyararşinin yukarından aşağı olacak şekilde ayrılarak yazılmalıdır.
* user_migration.py dosyasında yer alan aşağıdaki değişkenlerin varolan OpenLDAP erişim bilgilerine göre düzenlenmelidir.
 


        self.base_dn = "dc=examle,dc=com"
        self.ldap_admin_dn = "cn=admin,"+str(self.base_dn)
        self.pwd = "secret"
        self.ldap_server = "192.168.*.*"
        
* **python3 user_migration.py**  kodu ile çalıştırılır.
