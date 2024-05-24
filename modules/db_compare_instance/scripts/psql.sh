
#!/bin/sh
amazon-linux-extras install -y postgresql13
 
cp /var/lib/cloud/instance/scripts/db_compare.sh /home/db_compare.sh
chmod 755 /home/db_compare.sh
cp /var/lib/cloud/instance/scripts/db_config.sh /home/db_config.sh
chmod 755 /home/db_config.sh