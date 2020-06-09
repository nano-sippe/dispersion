from git import Repo
import argparse

def getParser():
    parser = argparse.ArgumentParser(description='clone the rerfactive index '\
                                     'info database')
    parser.add_argument('--install_dir', default=None, type=str)
    return parser

if __name__ == "__main__":
    args = getParser().parse_args()
    git_url = "https://github.com/polyanskiy/refractiveindex.info-database.git"
    Repo.clone_from(git_url, args.install_dir)
