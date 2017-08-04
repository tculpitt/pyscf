from pyscf.ci import cisd
from pyscf.ci import ucisd

def CISD(mf, frozen=[], mo_coeff=None, mo_occ=None):
    from pyscf import lib
    from pyscf import scf
    if isinstance(mf, scf.uhf.UHF):
        if len(frozen) == 0:
            frozen = [[],[]]
        return ucisd.UCISD(mf, frozen, mo_coeff, mo_occ)
    elif isinstance(mf, scf.rohf.ROHF):
        lib.logger.warn(mf, 'RCISD method does not support ROHF method. ROHF object '
                        'is converted to UHF object and UCISD method is called.')
        mf = scf.addons.convert_to_uhf(mf)
        return ucisd.UCISD(mf, [frozen,frozen], mo_coeff, mo_occ)
    else:
        return cisd.CISD(mf, frozen, mo_coeff, mo_occ)
