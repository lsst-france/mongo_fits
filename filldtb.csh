#! /usr/local/bin/csh 

#$ -S "/usr/local/bin/csh" 

# pour nommer le job
#$ -N filldtb

# pour declarer votre projet sous lequel le job sera execute
#$ -P P_lsst

# pour fusionner les sorties stdout et stderr dans un seul fichier
#$ -j y
#$ -l sps=1

# les sorties stdout et stderr se trouveront par defaut dans votre $HOME
# pour les placer ailleurs par ex. sous votre $HOME :
#$ -o $HOME/mongo_fits/log

# executer votre commande, et sauvegarder le resultat 

cd /afs/in2p3.fr/home/a/arnault/mongo_fits
source setup.csh

python --version

python fits.py


