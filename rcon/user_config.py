from rcon.models import UserConfig, enter_session

def _get_conf(sess, key):
    return sess.query(UserConfig).filter(UserConfig.key == key).one_or_none()

def get_user_config(key, default=None):
    with enter_session() as sess:
        res = _get_conf(sess, key)
        return res.value if res else default
    
def _add_conf(sess, key, val):
    return sess.add(UserConfig(
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

class WelcomeMessage:
    ON_MAP_CHANGE = 'welcome_message_on_map_change'
    ON_INTERVAL_SWITCH = 'welcome_message_on_interval_switch'
    ON_INTERVAL_PERIOD = 'welcome_message_on_interval_period'
    ON_INTERVAL_UNIT = 'welcome_message_on_interval_unit'
    WELCOME_MESSAGE = 'welcome_message'

    def __init__(self):
        pass

    def seed_db(self, sess):
        if _get_conf(sess, self.ON_MAP_CHANGE) is None:
            _add_conf(sess, self.ON_MAP_CHANGE, False)
        if _get_conf(sess, self.ON_INTERVAL_SWITCH) is None:
            _add_conf(sess, self.ON_INTERVAL_SWITCH, False)
        if _get_conf(sess, self.ON_INTERVAL_PERIOD) is None:
            _add_conf(sess, self.ON_INTERVAL_PERIOD, 0)
        if _get_conf(sess, self.ON_INTERVAL_UNIT) is None:
            _add_conf(sess, self.ON_INTERVAL_UNIT, "minutes")
        if _get_conf(sess, self.WELCOME_MESSAGE) is None:
            _add_conf(sess, self.WELCOME_MESSAGE, "")

    def get_on_map_change(self):
        return get_user_config(self.ON_MAP_CHANGE)

    def set_on_map_change(self, on_map_change):
        if not isinstance(on_map_change, bool):
            raise InvalidConfigurationError("On map change must be a bool")
        set_user_config(self.ON_MAP_CHANGE, on_map_change)

    def get_on_interval_switch(self):
        return get_user_config(self.ON_INTERVAL_SWITCH)

    def set_on_interval_switch(self, on_interval_switch):
        if not isinstance(on_interval_switch, bool):
            raise InvalidConfigurationError("On interval switch must be a bool")
        set_user_config(self.ON_INTERVAL_SWITCH, on_interval_switch)

    def get_on_interval_period(self):
        return get_user_config(self.ON_INTERVAL_PERIOD)

    def set_on_interval_period(self, on_interval_period):
        if not int(on_interval_period) > 0:
            raise InvalidConfigurationError("On interval period must be an int bigger than 0")
        set_user_config(self.ON_INTERVAL_PERIOD, int(on_interval_period))

    def get_on_interval_unit(self):
        return get_user_config(self.ON_INTERVAL_UNIT)

    def set_on_interval_unit(self, on_interval_unit):
        if not on_interval_unit in ["seconds", "minutes", "hours"]:
            raise InvalidConfigurationError("On interval unit must be seconds, minutes or hours")

    def get_welcome(self):
        return get_user_config(self.WELCOME_MESSAGE)

    def set_welcome(self, welcome):
        if not isinstance(welcome, str):
            raise InvalidConfigurationError("Welcome message must be a string")
        set_user_config(self.WELCOME_MESSAGE, welcome) 


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
            m = m.replace('\\n', '\n')
            if isinstance(m, str):
                m = m.split(' ', 1)
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
            msgs.append((time, msg))

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
        WelcomeMessage().seed_db(sess)
        sess.commit()
