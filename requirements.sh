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
elif [ "$dist" == "Raspbian" ]; then
    # Can't do 'sudo' with standard MSM install on a Mark 1 or Picroft,
    # use pkcon instead which doesn't need sudo
    msm install https://github.com/JarbasAl/skill-camera
    for dep in "${dependencies[@]}"
    do
        pkcon install $dep
    done
    exit
fi



# installing dependencies
for dep in "${dependencies[@]}"
do
    sudo $pm $dep
done

# camera skill is also needed

sudo msm install https://github.com/JarbasAl/skill-camera

#git clone https://github.com/davisking/dlib.git
#cd dlib
#mkdir build; cd build; cmake .. -DDLIB_USE_CUDA=0 -DUSE_AVX_INSTRUCTIONS=1; cmake --build .
#cd ..
#python setup.py install --no USE_AVX_INSTRUCTIONS --no DLIB_USE_CUDA
