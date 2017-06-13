git clone https://github.com/davisking/dlib.git
cd dlib
mkdir build; cd build; cmake .. -DDLIB_USE_CUDA=0 -DUSE_AVX_INSTRUCTIONS=1; cmake --build .
cd ..
python setup.py install --no USE_AVX_INSTRUCTIONS --no DLIB_USE_CUDA