'''
Interface for PySCF and ASE
'''

from ase.calculators.calculator import Calculator
from ase.units import Bohr, Hartree
from pyscf.data import nist
from pyscf import neo
from pyscf import gto, dft
from pyscf.scf.hf import dip_moment

class Pyscf_NEO(Calculator):

    implemented_properties = ['energy', 'forces', 'dipole']
    default_parameters = {'basis': 'ccpvdz',
                          'charge': 0,
                          'spin': 0,
                          'xc': 'b3lyp',
                          'quantum_nuc': 'all'}


    def __init__(self, **kwargs):
        Calculator.__init__(self, **kwargs)

    def calculate(self, atoms=None, properties=['energy', 'forces', 'dipole'],
                  system_changes=['positions', 'numbers', 'cell', 'pbc', 'charges', 'magmoms']):
        Calculator.calculate(self, atoms, properties, system_changes)
        mol = neo.Mole()
        atoms = self.atoms.get_chemical_symbols()
        positions = self.atoms.get_positions()
        mol.atom = []
        for i in range(len(atoms)):
            if atoms[i] == 'Mu':
                mol.atom.append(['H@0', tuple(positions[i])])
            elif atoms[i] == 'D':
                mol.atom.append(['H@2', tuple(positions[i])])
            else:
                mol.atom.append(['%s%i' %(atoms[i],i), tuple(positions[i])])
        mol.basis = self.parameters.basis
        mol.build(quantum_nuc = self.parameters.quantum_nuc,
                  charge = self.parameters.charge, spin = self.parameters.spin)
        if self.parameters.spin == 0:
            mf = neo.CDFT(mol)
        else:
            mf = neo.CDFT(mol, unrestricted = True)
        mf.mf_elec.xc = self.parameters.xc
        self.results['energy'] = mf.scf()*Hartree
        g = mf.Gradients()
        self.results['forces'] = -g.grad()*Hartree/Bohr

        dip_elec = dip_moment(mol.elec, mf.mf_elec.make_rdm1()) # dipole of electrons and classical nuclei
        dip_nuc = 0
        for i in range(len(mf.mf_nuc)):
            ia = mf.mf_nuc[i].mol.atom_index
            dip_nuc += mol.atom_charge(ia) * mf.mf_nuc[i].nuclei_expect_position * nist.AU2DEBYE

        self.results['dipole'] = dip_elec + dip_nuc


class Pyscf_DFT(Calculator):

    implemented_properties = ['energy', 'forces', 'dipole']
    default_parameters = {'mf':'RKS',
                          'basis': 'ccpvdz',
                          'charge': 0,
                          'spin': 0,
                          'xc': 'b3lyp',
                          }


    def __init__(self, **kwargs):
        Calculator.__init__(self, **kwargs)

    def calculate(self, atoms=None, properties=['energy', 'forces', 'dipole'],
                  system_changes=['positions', 'numbers', 'cell', 'pbc', 'charges', 'magmoms']):
        Calculator.calculate(self, atoms, properties, system_changes)
        mol = gto.Mole()
        atoms = self.atoms.get_chemical_symbols()
        positions = self.atoms.get_positions()
        mol.atom = []
        for i in range(len(atoms)):
            if atoms[i] == 'D':
                mol.atom.append(['H@2', tuple(positions[i])])
            else:
                mol.atom.append(['%s' %(atoms[i]), tuple(positions[i])])
        mol.basis = self.parameters.basis
        mol.build(charge = self.parameters.charge, spin = self.parameters.spin)
        if self.parameters.spin != 0:
            mf = dft.UKS(mol)
        else:
            mf = dft.RKS(mol)
        mf.xc = self.parameters.xc
        self.results['energy'] = mf.scf()*Hartree
        g = mf.Gradients()
        self.results['forces'] = -g.grad()*Hartree/Bohr
        self.results['dipole'] = dip_moment(mol, mf.make_rdm1())


