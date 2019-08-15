def collect_roles_perms(role):
    perm = []
    try:
        for r in role:
            perm += list(r.perms.values('id', 'codename'))
    except Exception as e:
        pass
    # 去掉重复权限
    perms = set()
    new_perms = []
    for p in perm:
        t = tuple(p.items())
        if t not in perms:
            perms.add(t)
            new_perms.append(p)
    return new_perms


def collect_roles_routers(role):
    router = []
    try:
        for r in role:
            router += list(r.routers.values())
    except Exception as e:
        pass
    # 去掉重复权限
    routers = set()
    new_routers = []
    if len(router) != 0:
        for p in router:
            t = tuple(p.items())
            if t not in routers:
                routers.add(t)
                new_routers.append(p)
    return new_routers
