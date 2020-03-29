from rcon.models import UserConfig, enter_session

def _get_conf(sess, key):
    return sess.query(UserConfig).filter(UserConfig.key == key).one_or_none()

def get_user_config(key, default=None):
    with enter_session() as sess:
        res = _get_conf(sess, key)
        return res.value if res else default
    
def _add_conf(sess, key, val):
    res = sess.add(UserConfig(
            key=key,
            value=val
        ))

def set_user_config(key, object_):
    with enter_session() as sess:
        conf = _get_conf(sess, key)
        if conf is None:
            _add_conf(sess, key, object_)
        else:
            conf.value = object_
        sess.commit()


class InvalidConfigurationError(Exception):
    pass

class AutoBroadcasts:
    BROADCASTS_RANDOMIZE = 'broadcasts_randomize'
    BROADCASTS_MESSAGES = 'broadcasts_messages'
    BROADCASTS_ENABLED = 'broadcasts_enabled'
    
    def __init__(self):
        pass

    def seed_db(self, sess):
        if _get_conf(sess, self.BROADCASTS_RANDOMIZE) is None:
            _add_conf(sess, self.BROADCASTS_RANDOMIZE, False)
        if _get_conf(sess, self.BROADCASTS_MESSAGES) is None:
            _add_conf(sess, self.BROADCASTS_MESSAGES, [])
        if _get_conf(sess, self.BROADCASTS_ENABLED) is None:
            _add_conf(sess, self.BROADCASTS_ENABLED, False)

    def get_messages(self):
        return get_user_config(self.BROADCASTS_MESSAGES)
    
    def set_messages(self, messages):
        msgs = []

        for m in messages:
            if len(m) != 2:
                raise InvalidConfigurationError(
                    "Broacast message must be tuples (<int: seconds>, <str: message>)"
                )
            time, msg = m
            try: 
                time = int(time)
                if time <= 0:
                    raise ValueError("Negative")
            except ValueError as e:
                raise InvalidConfigurationError(
                    "Time must be an positive integer"
                ) from e

        set_user_config(self.BROADCASTS_MESSAGES, msgs)
        
    def get_randomize(self):
        return get_user_config(self.BROADCASTS_RANDOMIZE)
    
    def set_randomize(self, bool_):
        if not isinstance(bool_, bool):
            raise InvalidConfigurationError("Radomize must be a boolean")
        return set_user_config(self.BROADCASTS_RANDOMIZE, bool_)

    def get_enabled(self):
        return get_user_config(self.BROADCASTS_ENABLED)

    def set_enabled(self, bool_):
        if not isinstance(bool_, bool):
            raise InvalidConfigurationError("Enabled must be a boolean")
        return set_user_config(self.BROADCASTS_ENABLED, bool_)

def seed_default_config():
    with enter_session() as sess:
        AutoBroadcasts().seed_db(sess)
        sess.commit()
