if [ "$SERVER_NUMBER" == '1' ]
then
chown root:root /config/logrotate.conf
/usr/sbin/logrotate /config/logrotate.conf
fi 