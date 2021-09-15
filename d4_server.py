# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse;
import pyBigWig
import json
import ctypes
import math

hostName = "localhost"
serverPort = 8888


# /Users/jrobinso/igv-team%20Dropbox/Data/Juicebox/CTCF_Untreated.bw

class BigwigServer(BaseHTTPRequestHandler):

    def do_GET(self):

        # Initial assumptions, until proven otherwise
        start = 0
        values = None
        nvalues = 0

        # Parse file path and query parameters
        parsed = urlparse(self.path)
        query = parsed.query
        filepath = parsed.path.replace("%20", " ");

        if query is not None and len(query) > 0:
            query_components = dict(qc.split("=") for qc in query.split("&"))

            if "class" in query_components and query_components["class"] == "header":
                self.do_headerquery(filepath)

            elif "chr" in query_components:
                self.do_dataquery(filepath, query_components)

            else:
                self.do_nullresponse(query)
        else:
            self.do_nullresponse(None)

    # Return some meta information about the file.  Currently jsut returns chromosome names as a json array
    # This is needed to support IGV chr name aliasing
    def do_headerquery(self, filepath):
        bw = pyBigWig.open(filepath)
        chrom_dict = bw.chroms();
        chrom_names = list(chrom_dict.keys())
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(chrom_names), "utf-8"))
        self.wfile.flush();

    def do_dataquery(self, filepath, query_components):
        chr = query_components["chr"]
        start = max(0, int(query_components["start"]))
        end = max(0, int(query_components["end"]))

        try:
            # Open bigwig file and retrieve values
            bw = pyBigWig.open(filepath)
            chrom_dict = bw.chroms();
            if chr in chrom_dict:
                maxpos = chrom_dict[chr]
                end = min(end, maxpos)

                # Should we use summary stats (zoomLevel) or raw values?
                n = end - start
                if n > 1000:
                    stepsize = math.ceil(n / 1000)
                    nbins = math.floor(n / stepsize)
                    end = start + nbins*stepsize
                    values = bw.stats(chr, start, end, nBins=nbins)
                else:
                    end = min(end, maxpos)
                    values = bw.values(chr, start, end)
                    stepsize = 1

                nvalues = len(values)

                self.send_response(200)
                self.send_header("Content-type", "application/octect-stream")
                self.end_headers()
                self.wfile.write(start.to_bytes(4, 'little'))
                self.wfile.write(stepsize.to_bytes(4, 'little'))
                self.wfile.write(nvalues.to_bytes(4, 'little'))

                # Return values in binary format.
                buf = (ctypes.c_float * nvalues)()
                buf[:] = values

                self.wfile.write(buf)
                self.wfile.flush()

            else:
                self.do_nullresponse()

        except Exception as e:
            # TODO -- send error code and message ?
            self.do_nullresponse()


    def do_nullresponse(self):
        zero = 0
        self.send_response(200)
        self.send_header("Content-type", "application/octect-stream")
        self.end_headers()
        self.wfile.write(zero.to_bytes(4, 'little'))
        self.wfile.write(zero.to_bytes(4, 'little'))
        self.wfile.write(zero.to_bytes(4, 'little'))

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()



if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), BigwigServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")