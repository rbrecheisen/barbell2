import os
import util


def main():
    parser = util.get_parser()
    parser.add_argument('--directory', help='Path to directory', required=True)
    parser.add_argument('--recursive', help='Search recursively or not', type=int, default=0)
    parser.add_argument('--output_file', help='Path to text file containing file paths', default='files.txt')
    args = parser.parse_args()
    files = []
    if args.recursive > 0:
        for root, dirs, files in os.walk(args.directory):
            for f in files:
                files.append(os.path.join(root, f))
    else:
        for f in os.listdir(args.directory):
            files.append(os.path.join(args.directory, f))
    with open(args.output_file, 'w') as f:
        for item in files:
            f.write(item + '\n')


if __name__ == '__main__':
    main()
