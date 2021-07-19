def test_apply_changes_in_cache(prefilled_infra):
    (memory_db, cache), node1_idx, *_ = prefilled_infra
    node1 = cache.load(node1_idx)
    cache.delete(node1_idx)

    node = cache.find(node1_idx)
    assert node
    assert node.archive
