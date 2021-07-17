if [ "$SERVER_NUMBER" == '1' ]
then
chown root:root /config/logrotate.conf
/usr/sbin/logrotate -f /config/logrotate.conf
fi 