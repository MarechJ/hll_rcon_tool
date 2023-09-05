import logging

from rcon.models import UserConfig, enter_session

logger = logging.getLogger(__name__)


class InvalidConfigurationError(Exception):
    pass


def _get_conf(sess, key):
    return sess.query(UserConfig).filter(UserConfig.key == key).one_or_none()


def get_user_config(key, default=None) -> bool:
    logger.debug("Getting user config for %s", key)
    with enter_session() as sess:
        res = _get_conf(sess, key)
        res = res.value if res else default
        logger.debug("User config for %s is %s", key, res)
        return res


def _add_conf(sess, key, val):
    return sess.add(UserConfig(key=key, value=val))


def _set_default(sess, key, val):
    if _get_conf(sess, key) is None:
        _add_conf(sess, key, val)
    return val


def set_user_config(key, object_):
    logger.debug("Setting user config for %s with %s", key, object_)
    with enter_session() as sess:
        conf = _get_conf(sess, key)
        if conf is None:
            _add_conf(sess, key, object_)
        else:
            conf.value = object_
        sess.commit()
