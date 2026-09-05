# Update latest ubuntu packages
apt-get update
apt-get install -y curl git-core

# Install and enable git lfs
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash && apt-get install -y git-lfs && git lfs install

# Set up ssh key to connect to github
mkdir -p ~/.ssh && chmod 700 ~/.ssh

cat > ~/.ssh/id_ed25519_vast <<- EOM
-----BEGIN OPENSSH PRIVATE KEY-----
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKiPge9af/6OK+hqIJdku/nk2UiH11nOs2GL/v+238c2 dangquanghung27112000@gmail.com
-----END OPENSSH PRIVATE KEY-----
EOM

chmod 400 ~/.ssh/id_ed25519

ssh-keygen -F github.com || ssh-keyscan github.com >> ~/.ssh/known_hosts

git config --global user.email "hungdangkg@gmail.com"
git config --global user.name "HungDangQuang"

# Download COCO dataset
# wget http://images.cocodataset.org/zips/train2017.zip
# wget http://images.cocodataset.org/zips/val2017.zip
# wget http://images.cocodataset.org/annotations/annotations_trainval2017.zip

# Create target directory
# mkdir -p coco_2017
# mkdir -p coco_2017/annotations

# Unzip into coco_dataset/
unzip train2017.zip -d coco_2017/
unzip val2017.zip -d coco_2017/
unzip annotations_trainval2017.zip -d coco_2017/

# Clone a repo
git clone https://github.com/HungDangQuang/skin-cancer-detector.git
cd skin-cancer-detector
pip install -r requirements.txt 
cd models/GroundingDINO/ops
python setup.py build install
# python test.py
cd ../../..
