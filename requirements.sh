rundir=$(pwd)
if ! git clone https://github.com/davisking/dlib.git ; then
  echo "Unable to clone Dlib!"
  exit 4 
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
  exit 16
fi
