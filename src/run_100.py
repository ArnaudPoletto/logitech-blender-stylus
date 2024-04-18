import os

if __name__ == '__main__':
    for _ in range(100):
        os.system('blender ../data/base_multi.blend --python run.py -- -r True')
