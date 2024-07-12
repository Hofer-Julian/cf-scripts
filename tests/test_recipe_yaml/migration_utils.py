from conda_forge_tick.migrators.core import Migrator


def run_test_migration(
    m: Migrator,
    inp: str,
    output: str,
    kwargs: dict,
    prb: dict,
    mr_out: dict,
    should_filter=False,
    tmpdir=None,
    make_body=False,
):
    if mr_out:
        mr_out.update(bot_rerun=False)
    with open(os.path.join(tmpdir, "meta.yaml"), "w") as f:
        f.write(inp)

    # read the conda-forge.yml
    if os.path.exists(os.path.join(tmpdir, "..", "conda-forge.yml")):
        with open(os.path.join(tmpdir, "..", "conda-forge.yml")) as fp:
            cf_yml = fp.read()
    else:
        cf_yml = "{}"

    # Load the meta.yaml (this is done in the graph)
    try:
        name = parse_meta_yaml(inp)["package"]["name"]
    except Exception:
        name = "blah"

    pmy = populate_feedstock_attributes(name, {}, inp, cf_yml)

    # these are here for legacy migrators
    pmy["version"] = pmy["meta_yaml"]["package"]["version"]
    pmy["req"] = set()
    for k in ["build", "host", "run"]:
        req = pmy["meta_yaml"].get("requirements", {}) or {}
        _set = req.get(k) or set()
        pmy["req"] |= set(_set)
    pmy["raw_meta_yaml"] = inp
    pmy.update(kwargs)

    try:
        if "new_version" in kwargs:
            pmy["version_pr_info"] = {"new_version": kwargs["new_version"]}
        assert m.filter(pmy) is should_filter
    finally:
        pmy.pop("version_pr_info", None)
    if should_filter:
        return pmy

    m.run_pre_piggyback_migrations(
        tmpdir,
        pmy,
        hash_type=pmy.get("hash_type", "sha256"),
    )
    mr = m.migrate(tmpdir, pmy, hash_type=pmy.get("hash_type", "sha256"))
    m.run_post_piggyback_migrations(
        tmpdir,
        pmy,
        hash_type=pmy.get("hash_type", "sha256"),
    )

    if make_body:
        fctx = FeedstockContext(
            feedstock_name=name,
            attrs=pmy,
        )
        fctx.feedstock_dir = os.path.dirname(tmpdir)
        m.effective_graph.add_node(name)
        m.effective_graph.nodes[name]["payload"] = MockLazyJson({})
        m.pr_body(fctx)

    assert mr_out == mr
    if not mr:
        return pmy

    pmy["pr_info"] = {}
    pmy["pr_info"].update(PRed=[frozen_to_json_friendly(mr)])
    with open(os.path.join(tmpdir, "meta.yaml")) as f:
        actual_output = f.read()
    # strip jinja comments
    pat = re.compile(r"{#.*#}")
    actual_output = pat.sub("", actual_output)
    output = pat.sub("", output)
    assert actual_output == output
    # TODO: fix subgraph here (need this to be xsh file)
    if isinstance(m, Version):
        pass
    else:
        assert prb in m.pr_body(None)
    try:
        if "new_version" in kwargs:
            pmy["version_pr_info"] = {"new_version": kwargs["new_version"]}
        assert m.filter(pmy) is True
    finally:
        pmy.pop("version_pr_info", None)

    return pmy
