from unittest.mock import Mock, call

from rcon.webhook_service import WebhookQueueKeyCache


def test_webhook_queue_key_cache_reuses_discovery_within_refresh_interval():
    red = Mock()
    red.scan_iter.side_effect = [
        iter([b"whs:list:1"]),
        iter([b"whs:transient_identifier:1"]),
        iter([b"whs:list:2"]),
        iter([]),
    ]
    red.llen.return_value = 1
    red.exists.return_value = 1
    cache = WebhookQueueKeyCache(red=red, refresh_interval_secs=1.0)

    expected = ["whs:list:1", "whs:transient_identifier:1"]
    assert cache.get_not_empty(now=10.0) == expected
    assert cache.get_not_empty(now=10.5) == expected
    assert red.scan_iter.call_args_list == [
        call(match="whs*", _type="list"),
        call(match="whs*", _type="string"),
    ]

    assert cache.get_not_empty(now=11.0) == ["whs:list:2"]
    assert red.scan_iter.call_count == 4


def test_webhook_queue_key_cache_filters_queues_deleted_between_scans():
    red = Mock()
    red.scan_iter.side_effect = [
        iter([b"whs:list:1"]),
        iter([b"whs:transient_identifier:1"]),
    ]
    red.llen.side_effect = [1, 0]
    red.exists.side_effect = [1, 0]
    cache = WebhookQueueKeyCache(red=red, refresh_interval_secs=1.0)

    assert cache.get_not_empty(now=10.0) == [
        "whs:list:1",
        "whs:transient_identifier:1",
    ]
    assert cache.get_not_empty(now=10.5) == []
    assert red.scan_iter.call_count == 2
