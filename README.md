# ctfetch
Fetch direct links from ctfile

## Requisitions
Python3

## Usage
Use download softwares like `aria2c -i urllist.txt` to start download.
You can also run `ctfetch` inline `aria2c ${ctfetch -n 16 url}`,
but it's not recommended since you need to re-fetch everytime you
run this command.

```
usage: ctfetch [-n N] [-o urllist.txt] url

positional arguments:
  url

optional arguments:
  -h, --help            show this help message and exit
  -n N, --num-user-agent N
                        Number of user agents to use. default max.
  -o OUTPUT, --output OUTPUT
                        Output file name. default to stdout.
```
