import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--major-minor', help='Major, minor or patch version upgrade', default='minor')
args = parser.parse_args()

f = open('VERSION', 'r')
version = f.readline().strip().split('.')
f.close()
v_major = int(version[0])
v_minor = int(version[1])
v_patch = int(version[2])
if args.major_minor == 'major':
    v_major += 1
elif args.major_minor == 'minor':
    v_minor += 1
elif args.major_minor == 'patch':
    v_patch += 1
f = open('VERSION', 'w')
f.write(f'{v_major}.{v_minor}.{v_patch}')
f.close()
