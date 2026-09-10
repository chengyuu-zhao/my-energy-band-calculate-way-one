import numpy as np
import matplotlib.pyplot as plt

def get_fermi_from_outcar(outcar_name="OUTCAR"):
    try:
        with open(outcar_name, "r") as f:
            for line in f:
                if "E-fermi" in line:
                    ef = float(line.split()[2])
                    print(f"✅ 从OUTCAR读取费米能级 Ef = {ef:.4f} eV")
                    return ef
    except FileNotFoundError:
        print("⚠️ 未找到OUTCAR，不做费米能级平移")
    return None


def read_eigenval_spin(filename="EIGENVAL"):
    f = open(filename, 'r')
    # 跳过前面注释文本行（CAR、system name等）
    while True:
        line = f.readline()
        if not line:
            raise Exception("EIGENVAL文件过早结束")
        parts = line.strip().split()
        if len(parts) == 3:
            try:
                nelect = int(parts[0])
                nkpts = int(parts[1])
                nbands = int(parts[2])
                break
            except ValueError:
                continue
    print(f"✅ EIGENVAL读取成功：NELECT={nelect}, NKPTS={nkpts}, NBANDS={nbands}")

    kx = np.zeros(nkpts)
    ky = np.zeros(nkpts)
    kz = np.zeros(nkpts)
    e_up = np.zeros((nkpts, nbands))
    e_dn = np.zeros((nkpts, nbands))

    for ik in range(nkpts):
        # 读取k点，跳过无效文本行
        while True:
            line = f.readline()
            if not line:
                raise Exception("文件读到k点时提前结束")
            parts = line.strip().split()
            if len(parts)>=4:
                try:
                    kx[ik] = float(parts[0])
                    ky[ik] = float(parts[1])
                    kz[ik] = float(parts[2])
                    break
                except ValueError:
                    continue
        # 读取nbands条能级
        for ib in range(nbands):
            while True:
                line = f.readline()
                if not line:
                    raise Exception(f"kpoint {ik}, band {ib}: 文件提前结束")
                parts = line.strip().split()
                if len(parts)>=3:
                    try:
                        e_up[ik, ib] = float(parts[1])
                        e_dn[ik, ib] = float(parts[2])
                        break
                    except ValueError:
                        continue
    f.close()

    # kpath长度
    k_dist = np.zeros(nkpts)
    for i in range(1, nkpts):
        dk = np.sqrt((kx[i]-kx[i-1])**2 + (ky[i]-ky[i-1])**2 + (kz[i]-kz[i-1])**2)
        k_dist[i] = k_dist[i-1] + dk
    return k_dist, e_up, e_dn, nkpts, nbands


def plot_spin_band(k_dist, e_up, e_dn, efermi=None, ylim=None):
    plt.figure(figsize=(9,6))
    nbands = e_up.shape[1]
    for ib in range(nbands):
        if efermi is not None:
            plt.plot(k_dist, e_up[:,ib] - efermi, c="#2266bb", lw=1.1, label="spin up" if ib==0 else "")
        else:
            plt.plot(k_dist, e_up[:,ib], c="#2266bb", lw=1.1, label="spin up" if ib==0 else "")
    for ib in range(nbands):
        if efermi is not None:
            plt.plot(k_dist, e_dn[:,ib] - efermi, c="#dd3333", lw=1.1, linestyle="--", label="spin down" if ib==0 else "")
        else:
            plt.plot(k_dist, e_dn[:,ib], c="#dd3333", lw=1.1, linestyle="--", label="spin down" if ib==0 else "")

    if efermi is not None:
        plt.axhline(y=0, c="black", ls="--", lw=1.5, label="$E_F$")
        plt.ylabel("$E-E_F$ (eV)")
    else:
        plt.ylabel("$E$ (eV)")
    plt.xlabel("K-path")
    plt.grid(alpha=0.3)
    plt.legend(loc="best")
    if ylim:
        plt.ylim(ylim)
    plt.tight_layout()
    plt.savefig("band.png", dpi=300)  # 直接保存图片，解决Mac弹窗不显示问题
    print("✅ 能带图已保存为 band.png")
    plt.show()


if __name__ == "__main__":
    ef = get_fermi_from_outcar("OUTCAR")
    k_dist, e_up, e_dn, nkpts, nbands = read_eigenval_spin("EIGENVAL")
    print(f"k点数量={nkpts}, 每个k点能带数={nbands}")
    y_range = [-1, 1]
    plot_spin_band(k_dist, e_up, e_dn, efermi=ef, ylim=y_range)
