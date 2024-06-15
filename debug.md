发生异常: HTTPError
502 Server Error: Bad Gateway for url: https://api.planet.com/basemaps/v1/mosaics/c2446a6b-ec1e-439e-9b0b-2dab900375f0/quads/search?v=1.5
  File "/Users/zgf/Downloads/同步空间/毕业设计/tools/planetdownload copy.py", line 200, in _post
    rv.raise_for_status()
  File "/Users/zgf/Downloads/同步空间/毕业设计/tools/planetdownload copy.py", line 173, in _query
    response = self._post(url, json_query)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zgf/Downloads/同步空间/毕业设计/tools/planetdownload copy.py", line 326, in quads
    for info in quads:
  File "/Users/zgf/Downloads/同步空间/毕业设计/tools/planetdownload copy.py", line 97, in _chunks
    v = tuple(it.islice(iterable, chunksize))
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zgf/Downloads/同步空间/毕业设计/tools/planetdownload copy.py", line 381, in download_quads
    for group in groups:
  File "/Users/zgf/Downloads/同步空间/毕业设计/tools/planetdownload copy.py", line 83, in main
    for item in files:
  File "/Users/zgf/Downloads/同步空间/毕业设计/tools/planetdownload copy.py", line 535, in <module>
    main()
requests.exceptions.HTTPError: 502 Server Error: Bad Gateway for url: https://api.planet.com/basemaps/v1/mosaics/c2446a6b-ec1e-439e-9b0b-2dab900375f0/quads/search?v=1.5