# d4server

Project for prototyping ideas for "D4 server".  Initially bigwig is used as a proxy for d4 files.

#### Installation

You need a recent version of python, tested with 3.9, and pip

```
pip install -r requirements.txt
python d4_server.py
```

The server will now be listening on port 8888.  You can change the port by editing d4_server.py



#### URL Syntax

The basic URL syntax to use with IGV is as follows

* scheme: htsget
* path:   full path to a bigwig file on the machine running the server.  Spaces should be percent encoded (```%20```)

Example

```
d4get://localhost:8888/Users/jrobinso/igv-team%20Dropbox/Data/Juicebox/CTCF_Untreated.bw
```

IGV assumes the transport protocol for the ```d4get``` scheme is http.  This is analogous to how the ```htsget``` scheme is handled.
If we retain the scheme-based syntax we might add ```d4gets``` to signal https protocol (with ```htsget``` we just assume https).

#### Response

The following isn't required for igv use, but might be useful for testing.  The server uses the GET method with parameters.
Parameters can be 

* none, in which case nothing is returned
* class=header,  which currently returns the chromosome names as a json array.  This is important for IGV to be able do chr name aliasing.
* chr=str&start=int&end=int,  data query, returns a binary response as described below.

Data query response is simply a binary stream of bytes in the following order.  In a real implementation we would gzip this.

* start (uint) - the genomic start position of the data, should be same as the query parameter
* step  (uint) - genomic step (bin) size for each data point
* npoints (uint) - the number of data points
* data (float) - array of float data

 

