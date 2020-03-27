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


RANDOMIZE_BROADCAST = 'randomize_broadcast'

def seed_default_config():
    with enter_session() as sess:
        random = _get_conf(sess, RANDOMIZE_BROADCAST)
        if random is None:
            _add_conf(sess, RANDOMIZE_BROADCAST, False)
        sess.commit()

if __name__ == "__main__":
    print(get_user_config(RANDOMIZE_BROADCAST))