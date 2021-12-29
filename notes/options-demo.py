#-------------------------------------------------------------------------------

g = group_by(tbl.cols["root"], tbl.cols["expiry"])
tbl.cols["max_vlt"] = g.aggregate(mean)(tbl["vlt"], tbl["oi"])

# Or...

c = tbl.cols
c.max_vlt = group_by(c.root, c.expiry).aggregate(mean)(c.vlt, c.oi)

# Or...

with tbl.cols:
    g = group_by(root, expiry)
    max_vlt = g.aggregate(weighted_mean)(vlt, oi)

#-------------------------------------------------------------------------------

tbl.cols["occ_root"] = compose(tbl.cols["eqid"], root_per_eqid)

