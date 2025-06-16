import numpy as np
from sklearn.metrics import confusion_matrix


def cohens_kappa(A, B):
    cm = confusion_matrix(A, B)
    N = cm.sum()
    p_0 = np.diag(cm).sum() / N
    p_c = 0.0
    for i in range(cm.shape[0]):
        p_c += cm[i, :].sum() * cm[:, i].sum()
    p_c /= N**2
    return (p_0 - p_c) / (1.0 - p_c)


def src(smap, ldat, threshold, num=(20, 10), return_auc=False, nodata=0):
    """Remondo et al. 2003, validation curve"""

    if not isinstance(num, tuple):
        num = (num, num)
    w = int(smap.shape[0] // num[0])
    h = int(smap.shape[1] // num[1])
    offx = np.round(0.5 * (smap.shape[0] - w * num[0])).astype(int)
    offy = np.round(0.5 * (smap.shape[1] - h * num[1])).astype(int)

    smap = smap[offx : -offx - 1, offy : -offy - 1]
    ldat = ldat[offx : -offx - 1, offy : -offy - 1]

    M = np.sum(smap >= threshold)
    N = np.sum(ldat)  # number of landslides in this map
    assert N > 9

    x = []
    for i in range(0, smap.shape[0], w):
        for j in range(0, smap.shape[1], h):
            wnd = smap[i : i + w, j : j + h]
            zero_mask = wnd == 0
            if wnd.size == np.sum(zero_mask):
                continue
            n = np.sum(ldat[i : i + w, j : j + h])
            # x.append((wnd[~zero_mask].mean(), n / N))
            m = np.sum(wnd >= threshold)
            x.append((m / M, n / N))
    X = [xx for _, xx in sorted(x, key=lambda k: -k[0])]
    Y = np.full(len(x), 1 / len(x))
    y0 = np.cumsum(Y)
    y1 = np.cumsum(X)
    if return_auc:
        return y0, y1, np.sum(Y * y1)
    return y0, y1
