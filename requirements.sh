

# The requirements.sh is an advanced mechanism and should rarely be needed.
# Be aware that it won't run with root permissions and 'sudo' won't work
# in most cases.

#detect distribution using lsb_release (may be replaced parsing /etc/*release)
dist=$(lsb_release -d |awk '{print$2}')

dependencies=( build-essential cmake libgtk-3-dev libboost-all-dev )

#setting dependencies and package manager in relation to the distribution
if [ "$dist"  == "Arch"  ]; then
    pm="pacman -S"
elif [ "$dist" ==  "Ubuntu" ] || [ "$dist" == "KDE" ] || [ "$dist" == "Debian" ]; then
    pm="apt install"
fi


if [ "$dist" == "Raspbian" ]; then
    # installing dependencies without sudo
    for dep in "${dependencies[@]}"
    do
        pkcon install $dep
    done
elif [ "$dist" != "Raspbian" ]; then
    # installing dependencies
    for dep in "${dependencies[@]}"
    do
        sudo $pm $dep
    done
fi

# compile dlib
rundir=$(pwd)
if ! git clone https://github.com/davisking/dlib.git ; then
  echo "Unable to clone Dlib!"
  exit 0
fi
cd dlib
if grep -q avx /proc/cpuinfo ; then
  mkdir build; cd build; cmake .. -DDLIB_USE_CUDA=0 -DUSE_AVX_INSTRUCTIONS=1; cmake --build .
else
  mkdir build; cd build; cmake .. -DDLIB_USE_CUDA=0 ; cmake --build .
fi  
cd ${rundir}/dlib
if ! python setup.py install --no USE_AVX_INSTRUCTIONS --no DLIB_USE_CUDA ; then
  echo "Unable to install python Dlib!" 
  exit 0
fi

exit 0