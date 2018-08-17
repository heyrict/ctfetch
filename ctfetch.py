#!/usr/bin/env python3
"""
Fetch actual download links for ctfile.
Availables urls should like: https://*.ctfile.com/i/[0-9]*/f/[0-9A-Za-z]*
"""

import argparse
import random
import re
import sys
from json.decoder import JSONDecoder
from urllib.parse import urljoin
from urllib.request import Request, urlopen

USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.9 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36 OPR/48.0.2685.52',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.49 Safari/537.36 OPR/48.0.2685.7',
    'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0',
    'Mozilla/5.0 (X11; U; Linux x86_64; en-us) AppleWebKit/531.2+ (KHTML, like Gecko) Version/5.0 Safari/531.2',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36 OPR/47.0.2631.55',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0) Gecko/20100101 Firefox/56.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0.1 Safari/604.3.5',
    'Mozilla/5.0 (X11; CrOS armv7l 9592.96.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.114 Safari/537.36',
    'Mozilla/5.0 (OS/2; U; Warp 4.5; en-US; rv:1.7.12) Gecko/20050922 Firefox/1.0.7',
    'Mozilla/5.0 (X11; FreeBSD amd64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36',
    'Mozilla/5.0 (X11; U; FreeBSD i386; zh-tw; rv:31.0) Gecko/20100101 Opera/13.0',
    'Mozilla/5.0 (X11; FreeBSD amd64; rv:40.0) Gecko/20100101 Firefox/40.0',
]


def read_webpage(req):
    with urlopen(req) as f:
        content = f.read().decode('utf-8')
    return content


def parse_cmdline():
    parser = argparse.ArgumentParser(
        usage='%(prog)s [-n N] [-o urllist.txt] url',
        description='''\
            Fetching actual links from ctfile.
            Use download softwares like `aria2c -i urllist.txt` to start download.
        ''')
    parser.add_argument('url')
    parser.add_argument(
        '-n',
        '--num-user-agent',
        metavar='N',
        type=int,
        default=None,
        dest='numUserAgents',
        help='Number of user agents to use. default max.')
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        help='Output file name. default to stdout.')

    args = parser.parse_args()
    return args


def parse_params(pagesrc):
    """
    Get required params from webpage.
    """
    userid_list = re.findall(r'var userid = \'([0-9]+)\'', pagesrc)
    assert userid_list, 'Cannot find userid variable in the webpage.'
    userid = userid_list[0]

    free_down_funcstrs = re.findall(r'free_down\(([^)]+)\)', pagesrc)
    assert free_down_funcstrs, 'Cannot find free_down(...) function.'

    free_down_params = re.findall(r'[a-z0-9]+', free_down_funcstrs[0])
    file_id, folder_id, file_chk, mb, app = free_down_params[:5]

    verifycode = ''
    if len(free_down_params) >= 6:
        verifycode = free_down_params[6]

    return userid, file_id, folder_id, file_chk, mb, app, verifycode


def main():
    args = parse_cmdline()
    if args.output:
        output_stream = open(args.output, 'w')
    else:
        output_stream = sys.stdout

    results = []
    decoder = JSONDecoder()

    content = read_webpage(args.url)
    userid, file_id, folder_id, file_chk, mb, app, verifycode = parse_params(
        content)

    # Query get_file_url api for file link
    get_file_api = "/get_file_url.php?uid=%(userid)s&fid=%(file_id)s"\
            "&folder_id=%(folder_id)s&fid=%(file_id)s&file_chk=%(file_chk)s&mb=%(mb)s"\
            "&app=%(app)s&verifycode=%(verifycode)s&rd=%(rd)f" % {
                "userid": userid,
                "file_id": file_id,
                "folder_id": folder_id,
                "file_chk": file_chk,
                "mb": mb,
                "app": 0,
                "verifycode": verifycode,
                "rd" : random.random(),
            }

    for ua in USER_AGENT_LIST[:args.numUserAgents]:
        request = Request(
            urljoin(args.url, get_file_api), headers={
                'User-Agent': ua,
            })
        response_text = read_webpage(request)
        response_obj = decoder.decode(response_text)
        downurl = response_obj.get('downurl')
        if downurl:
            results.append(downurl)
            print(downurl, end='\t', file=output_stream)

    output_stream.close()


if __name__ == '__main__':
    main()
