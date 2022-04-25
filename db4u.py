import urllib.request
import zipfile
import os
import stat
import string
import random
import fileinput

#with urllib.request.urlopen('https://files.phpmyadmin.net/phpMyAdmin/5.1.3/phpMyAdmin-5.1.3-all-languages.zip') as f:
#    html = f.read().decode('utf-8')
#s = urllib.request.urlopen('https://files.phpmyadmin.net/phpMyAdmin/5.1.3/phpMyAdmin-5.1.3-all-languages.zip').read()

def replace(filename, text_to_search, replacement_text):
	with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
	    for line in file:
	        print(line.replace(text_to_search, replacement_text), end='')

def replace_append(filename, search, replacement,block):
	with open(filename, "r") as in_file:
	    buf = in_file.readlines()
	with open(filename+'.bkssl', "w") as bk_file:
	    bk_file.writelines(buf)

	with open(filename, "w") as out_file:
	    ext = False
	    for line in buf:
	        if search in line:
	            line = replacement
	            ext= True
	        out_file.write(line)
	    if not ext:
	        out_file.write(block)

def db4u():
	if  not os.path.exists('/usr/local/lsws/Example/phpMyAdmin'):
		url = 'https://files.phpmyadmin.net/phpMyAdmin/5.1.3/phpMyAdmin-5.1.3-all-languages.zip'
		urllib.request.urlretrieve(url, 'phpMyAdmin.zip')
		with zipfile.ZipFile('phpMyAdmin.zip', 'r') as zip_ref:
			zip_ref.extractall('./')
		if os.path.exists("phpMyAdmin.zip"):
			os.remove("phpMyAdmin.zip")
		else:
			print("The file does not exist")
		os.rename('./phpMyAdmin-5.1.3-all-languages','/usr/local/lsws/Example/phpMyAdmin')
		os.system("sudo chown -R www-data:www-data /usr/local/lsws/Example/phpMyAdmin")
		st = os.stat('/usr/local/lsws/Example/phpMyAdmin')
		os.chmod('/usr/local/lsws/Example/phpMyAdmin', st.st_mode | 0o755)
		return ('Installed Successfully')
	else:
		return ('Already Installed')

def vhost(domain):
	S = 10  # number of characters in the string.
	# call random.choices() string module to find the string in Uppercase + numeric data.
	password = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k = S))
	#username = (domain[:8]) if len(domain) > 8 else domain
	username = domain
	os.system("useradd -m -p "+password+" " + username)

	data = [username,password]

        ###### Default port 80 listener ###############
	filename = '/usr/local/lsws/conf/httpd_config.conf'
	search = 'listener Default{'
	replacement = '''listener Default{
	  map                     '''+domain+' '+domain
	replace(filename,search,replacement)

        ###### SSL port 443 listener ###############
	search = 'listener SSL {'
	replacement = '''listener SSL {
  map                     '''+domain+' '+domain+'\n'

	ful = '''
listener SSL {
  address                 *:443
  secure                  1
  keyFile                  /etc/letsencrypt/live/'''+domain+'''/privkey.pem
  certFile                 /etc/letsencrypt/live/'''+domain+'''/fullchain.pem
  certChain               1
  sslProtocol             24
  enableECDHE             1
  renegProtection         1
  sslSessionCache         1
  enableSpdy              15
  enableStapling           1
  ocspRespMaxAge           86400
  map                     '''+domain+' '+domain+'''
}
'''

	replace_append(filename,search,replacement,ful)

	########### Vhost entry #########
	vString='''

virtualHost '''+domain+''' {
  vhRoot                  /home/$VH_NAME
  configFile              $SERVER_ROOT/conf/vhosts/$VH_NAME/vhost.conf
  allowSymbolLink         1
  enableScript            1
  restrained              1
}

'''
	file_object = open(filename, 'a')
	file_object.write(vString)
	file_object.close()


	############ create  Vhost config folder ###################
	os.system("mkdir /usr/local/lsws/conf/vhosts/"+domain)

	############ create  Vhost config files ###################

	filename = "/usr/local/lsws/conf/vhosts/"+domain+"/vhost.conf"
	vConfig = '''
docRoot                   $VH_ROOT/public_html
vhDomain                  $VH_NAME
vhAliases                 www.$VH_NAME
adminEmails               info@inspedium.com
enableGzip                1
enableIpGeo               1

index  {
  useServer               0
  indexFiles              index.php, index.html
}

errorlog $VH_ROOT/logs/$VH_NAME.error_log {
  useServer               0
  logLevel                WARN
  rollingSize             10M
}

accesslog $VH_ROOT/logs/$VH_NAME.access_log {
  useServer               0
  logFormat               "%h %l %u %t "%r" %>s %b "%{Referer}i" "%{User-Agent}i""
  logHeaders              5
  rollingSize             10M
  keepDays                10
  compressArchive         1
}

errorpage 403 {
  url                     403.html
}

errorpage 404 {
  url                     404.html
}

errorpage 500 {
  url                     500.html
}

scripthandler  {
  add                     lsapi:'''+domain+''' php
}

extprocessor '''+domain+''' {
  type                    lsapi
  address                 UDS://tmp/lshttpd/'''+domain+'''.sock
maxConns                10
  env                     LSAPI_CHILDREN=10
  initTimeout             600
  retryTimeout            0
  persistConn             1
  pcKeepAliveTimeout      1
  respBuffer              0
  autoStart               1
  path                    /usr/local/lsws/lsphp74/bin/lsphp
  extUser                 '''+domain+'''
  extGroup                '''+domain+'''
  memSoftLimit            2047M
  memHardLimit            2047M
  procSoftLimit           400
  procHardLimit           500
}

phpIniOverride  {

}

module cache {
 storagePath /usr/local/lsws/cachedata/$VH_NAME
}

rewrite  {
 enable                  1
  autoLoadHtaccess        1
}

context /.well-known/acme-challenge {
  location                /usr/local/lsws/Example/html/.well-known/acme-challenge
  allowBrowse             1

  rewrite  {

  }
  addDefaultCharset       off

  phpIniOverride  {

  }
}

context /db4u {
  location                /usr/local/lsws/Example/phpMyAdmin
  allowBrowse             1

  rewrite  {

  }
  addDefaultCharset       off

  phpIniOverride  {

  }
}

vhssl  {
  keyFile                 /etc/letsencrypt/live/'''+domain+'''/privkey.pem
  certFile                /etc/letsencrypt/live/'''+domain+'''/fullchain.pem
  certChain               1
  sslProtocol             24
  enableECDHE             1
  renegProtection         1
  sslSessionCache         1
  enableSpdy              15
  enableStapling           1
  ocspRespMaxAge           86400
}
'''
	file_object = open(filename, 'w')
	file_object.write(vConfig)
	file_object.close()
	return(data)

def service_status(name):
	status = os.system('sudo systemctl is-active --quiet '+name)
	return (status)

def service_stop(name):
        status = os.system('sudo systemctl stop --quiet '+name)
        return (status)

def service_restart(name):
        status = os.system('sudo systemctl restart --quiet '+name)
        return (status)

def add_ssl(domain):
        status = os.system('sudo certbot certonly --webroot -w /usr/local/lsws/Example/html -d '+domain+',www.'+domain+' --email sarim@inspedium.com --agree-tos -n')
        return (status)
