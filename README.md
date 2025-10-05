
## Train

```
python scripts/gr00t_finetune.py --dataset-path /home/cwson/sandwich_raw_data --data-config so101 --output-dir /home/cwson/gr00t_output --num-gpus 1 --batch-size 2 --max-steps 3000 --use_mamba --tune_visual --learning-rate 1e-4 --video-backend torchvision_av --dataloader-num-workers 0 --report-to tensorboard
```


pyproject.toml  Update완료

Package                   Version            Editable project location
------------------------- ------------------ -------------------------------
absl-py                   2.3.1
accelerate                1.2.1
aiosignal                 1.4.0
albucore                  0.0.17
albumentations            1.4.18
annotated-types           0.7.0
antlr4-python3-runtime    4.9.3
attrs                     25.3.0
av                        12.3.0
blessings                 1.7
brotlicffi                1.0.9.2
certifi                   2025.8.3
cffi                      1.17.1
charset-normalizer        3.3.2
click                     8.3.0
cloudpickle               3.1.1
contourpy                 1.3.2
cramjam                   2.11.0
cycler                    0.12.1
decord                    0.6.0
diffusers                 0.35.1
dm-tree                   0.1.8
docker-pycreds            0.4.0
docstring_parser          0.17.0
einops                    0.8.1
eval_type_backport        0.2.2
exceptiongroup            1.3.0
Farama-Notifications      0.0.4
fastparquet               2024.11.0
filelock                  3.17.0
flash_attn                2.8.3
fonttools                 4.60.1
frozenlist                1.7.0
fsspec                    2024.6.1
fvcore                    0.1.5.post20221221
gitdb                     4.0.12
GitPython                 3.1.45
gmpy2                     2.2.1
gr00t                     1.1.0              /home/cwson/Isaac-GR00T-BiSO101
grpcio                    1.75.1
gymnasium                 1.0.0
h5py                      3.12.1
hf-xet                    1.1.10
huggingface-hub           0.35.3
hydra-core                1.3.2
idna                      3.7
imageio                   2.34.2
importlib_metadata        8.7.0
iniconfig                 2.1.0
iopath                    0.1.10
Jinja2                    3.1.6
jsonschema                4.25.1
jsonschema-specifications 2025.9.1
kiwisolver                1.4.9
kornia                    0.7.4
kornia_rs                 0.1.9
lazy_loader               0.4
llvmlite                  0.45.1
Markdown                  3.9
markdown-it-py            4.0.0
MarkupSafe                3.0.2
matplotlib                3.10.0
mdurl                     0.1.2
mkl_fft                   1.3.11
mkl_random                1.2.8
mkl-service               2.4.0
mpmath                    1.3.0
msgpack                   1.1.1
networkx                  3.4.2
numba                     0.62.1
numpy                     1.26.4
numpydantic               1.6.7
omegaconf                 2.3.0
onnx                      1.17.0
opencv-python-headless    4.11.0.86
packaging                 25.0
pandas                    2.3.3
peft                      0.17.0
pettingzoo                1.25.0
pillow                    11.3.0
pip                       25.2
platformdirs              4.4.0
pluggy                    1.6.0
portalocker               3.2.0
protobuf                  3.20.3
psutil                    7.1.0
pyarrow                   21.0.0
pycparser                 2.23
pydantic                  2.10.6
pydantic_core             2.27.2
Pygments                  2.19.2
pyparsing                 3.2.5
PySocks                   1.7.1
pytest                    8.4.2
python-dateutil           2.9.0.post0
pytorch3d                 0.7.8
pytz                      2025.2
PyYAML                    6.0.2
ray                       2.40.0
referencing               0.36.2
regex                     2025.9.18
requests                  2.32.3
rich                      14.1.0
rpds-py                   0.27.1
safetensors               0.6.2
scikit-image              0.25.2
scipy                     1.15.3
sentry-sdk                2.39.0
setproctitle              1.3.7
setuptools                78.1.1
shtab                     1.7.2
six                       1.17.0
smmap                     5.0.2
sympy                     1.13.1
tabulate                  0.9.0
tensorboard               2.20.0
tensorboard-data-server   0.7.2
termcolor                 3.1.0
tianshou                  0.5.1
tifffile                  2025.5.10
timm                      1.0.14
tokenizers                0.21.4
tomli                     2.2.1
torch                     2.5.1
torchaudio                2.5.1
torchvision               0.20.1
tqdm                      4.67.1
transformers              4.51.3
triton                    3.1.0
typeguard                 4.4.2
typing_extensions         4.12.2
tyro                      0.9.17
tzdata                    2025.2
urllib3                   2.5.0
wandb                     0.18.0
Werkzeug                  3.1.3
wheel                     0.45.1
yacs                      0.1.8
zipp                      3.23.0


git clone https://github.com/NVIDIA/Isaac-GR00T.git

git clone https://github.com/lmzpai/roboMamba.git

git clone https://github.com/KNU-BrainAI/KNU-Mamba.git

git clone https://github.com/jisuSong0625/Isaac-GR00T-BiSO101.git

git clone https://github.com/The-Swarm-Corporation/VLAM.git




# 현재 터미널 닫고 새로 열기, 또는
source ~/.bashrc
conda activate gr00t


conda create -n gr00t python=3.10
conda activate gr00t
pip install --upgrade setuptools
pip install -e .[base]
pip install --no-build-isolation flash-attn==2.7.1.post4 






# Isaac-GR00T-BiSO101에서 SO-101 설정 사용
cd /home/cwson/Isaac-GR00T-BiSO101
conda activate gr00t

python scripts/gr00t_finetune.py \
    --dataset-path /home/cwson/sandwich_raw_data \
    --data-config so101 \
    --num-gpus 1 \
    --batch-size 4 \
    --max-steps 3000 \
    --no-tune_diffusion_model \
    --learning-rate 1e-4


    # 홈 디렉토리로 출력 경로 변경
python scripts/gr00t_finetune.py \
    --dataset-path /home/cwson/sandwich_raw_data \
    --data-config so101 \
    --output-dir /home/cwson/gr00t_output \
    --num-gpus 1 \
    --batch-size 4 \
    --max-steps 3000 \
    --no-tune_diffusion_model \
    --learning-rate 1e-4




    python scripts/gr00t_finetune.py \
    --dataset-path /home/cwson/sandwich_raw_data \
    --data-config so101 \
    --output-dir /home/cwson/gr00t_output \
    --num-gpus 1 \
    --batch-size 4 \
    --max-steps 3000 \
    --no-tune_diffusion_model \
    --learning-rate 1e-4 \
    --video-backend torchcodec







conda create -n gr00t python=3.10 -y
# 4. 환경 활성화
conda activate gr00t
# 5. 필요한 패키지들 설치
pip install torch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
pip install accelerate==1.2.1 transformers==4.51.3 tokenizers==0.22.1
pip install numpy==1.26.4
# PyTorch 설치 (conda 사용)
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y
# 또는 pip 사용
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
# 호환되는 버전으로 설치
pip install accelerate==1.2.1 transformers==4.51.3 tokenizers==0.21.4

pip install tyro
pip install -e .
pip install decord
pip install "git+https://github.com/facebookresearch/pytorch3d.git"
pip install diffusers
pip install flash-attn --no-build-isolation

pip install --upgrade pandas pyarrow





export CUDA_VISIBLE_DEVICES=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

python scripts/gr00t_finetune.py \
    --dataset-path /home/cwson/sandwich_raw_data \
    --data-config so101 \
    --output-dir /home/cwson/gr00t_output \
    --num-gpus 1 \
    --batch-size 2 \
    --max-steps 3000 \
    --no-tune_diffusion_model \
    --learning-rate 1e-4 \
    --video-backend decord \
    --dataloader-num-workers 0





python scripts/gr00t_finetune.py --dataset-path /home/cwson/sandwich_raw_data --data-config so101 --output-dir /home/cwson/gr00t_output --num-gpus 1 --batch-size 2 --max-steps 3000 --use_mamba --tune_visual --learning-rate 1e-4 --video-backend torchvision_av --dataloader-num-workers 0 --report-to tensorboard