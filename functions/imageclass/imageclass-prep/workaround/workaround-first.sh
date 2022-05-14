#wget http://ftp.ch.debian.org/debian/pool/main/libs/libseccomp/libseccomp2_2.5.1-1_armhf.deb
#sudo dpkg -i libseccomp2_2.5.1-1_armhf.deb

#docker run -ti ubuntu:20.10 date
#docker run -ti --security-opt seccomp:unconfined ubuntu:20.10 date

sudo cp *.json /etc/docker
sudo service docker restart
