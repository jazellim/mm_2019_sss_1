import numpy as np

class Energy:

    def __init__(self, Geom, cutoff):
        self.Geom = Geom
        self.cutoff  = cutoff
        self.cutoff2 = self.cutoff**2

    def lennard_jones_potential(self,rij2):
        """
        Calculate Lennard-Jones Potential of particles.

        Parameters
        ----------
        rij2 : float or integer
            The square of the distance between particles i and j.

        Returns
        -------
        LJ: float
            Value of LJ potential.
        """

        sig_by_r6 = np.power(1 / rij2, 3)
        sig_by_r12 = np.power(sig_by_r6, 2)
        LJ = 4.0 * (sig_by_r12 - sig_by_r6)
        return LJ

    def get_particle_energy(self, i_particle, coordinates):
        """
        Calculate the energy of a particle with the remaining particles in the system

        Parameters
        ----------
        coordinates : numpy array(3xN). where 3 represents a column for each axis and N is the number of atoms
              coordinates given from xyz file or generated by generate_initial_state function.
        i_particle : integer, atom whose energy with the rest of the system is calculated
              Atom index (0-based) in the numpy array.

        Returns
        -------
        e_total : float
            Sum of the interaction energies between atom i and all other j atoms
        """

        r_i = coordinates[i_particle]
        rij2 = self.Geom.minimum_image_distance(r_i, coordinates)
        red = np.delete(rij2, i_particle)
        pot = self.lennard_jones_potential(red[red < self.cutoff2])
        e_total = pot.sum()
        return e_total

    def calculate_total_pair_energy(self):
        """
        Calculate total pair energy between particles i and j, iterated through all particle pairs in the system.

        Parameters
        ---------
        coordinates : array
            X, Y, Z coordinates of each particle in the system.
        cutoff2 : integer or float
            Square of the cutoff distance.

        Returns
        -------
        e_total : float
            Sum of all the pair energies between particles in the system that are within the cutoff distance.
        """

        e_total = 0.0
        particle_count = len(self.Geom.coordinates)
        for i_particle in range(particle_count):
            e_total += self.get_particle_energy(i_particle,self.Geom.coordinates)
        return e_total/2

    def calculate_tail_correction(self):
        """
        Calculate tail correction for Lennard-Jones potential.

        Parameters
        ----------
        num_particles : integer
            Number of particles in system.
        cutoff : integer or float
            Cutoff distance for the potential.
        volume : integer or float
            Volume of box in simulation.

        Returns
        -------
        e_correction : float
            Tail correction for num_particles in box of a given volume.
        """

        num_particles = self.Geom.num_particles
        sig_by_cutoff3 = np.power(1.0 / self.cutoff, 3)
        sig_by_cutoff9 = np.power(sig_by_cutoff3, 3)
        e_correction = sig_by_cutoff9 - 3.0 * sig_by_cutoff3
        e_correction *= 8.0 / 9.0 * np.pi * num_particles / self.Geom.volume * num_particles
        return e_correction
